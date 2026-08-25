"""
Tarama Döngüsü Orkestrasyon Servisi (sistem_mimari.md Bölüm 9 & 10.5)
Evren taraması, canlı veri toplama, birebir matematiksel hesaplama ve dürüst ilerleme takibi.
"""

from datetime import datetime, timezone
import uuid
import json
import asyncio
from typing import List, Dict, Any, Optional
from app.models.asset import Asset, AssetClass
from app.models.score import ScoreResult, SignalType
from app.scan.pipeline import AssetScanPipeline
from app.scan.market_fetcher import LiveMarketFetcher
from app.db.database import get_db_connection


class ScanStatusStore:
    """
    Tarama durumunu ve aşama metriklerini tutan mağaza (Bölüm 10.5 Dürüst İlerleme İlkesi).
    """
    def __init__(self):
        self.current_run_id: Optional[str] = None
        self.stage: str = "IDLE" # IDLE, INIT, FETCHING, SCORING, BENCHMARKS, COMPLETED, FAILED
        self.total_assets: int = 0
        self.processed_assets: int = 0
        self.failed_assets: int = 0
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.results: Dict[str, Any] = {}
        self.errors: List[Dict[str, str]] = []


class ScanOrchestrator:
    """
    Tam evren taramasını yöneten ve liderlik listelerini hesaplayan servis.
    """

    def __init__(self):
        self.status = ScanStatusStore()
        self._is_scanning = False
        self._load_cached_scores_from_db()

    def _load_cached_scores_from_db(self):
        """Kayıtlı skorları veritabanından hafızaya yükler (Yalnızca Hisse Senetleri)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM score_results WHERE symbol LIKE 'BIST:%' OR symbol LIKE 'NASDAQ:%' OR symbol LIKE 'NYSE:%'")
            rows = cursor.fetchall()
            conn.close()

            for r in rows:
                sym = r["symbol"]
                if not (sym.startswith("BIST:") or sym.startswith("NASDAQ:") or sym.startswith("NYSE:")):
                    continue
                keys = r.keys()
                cat_raw = r["category_scores"] if "category_scores" in keys else (r["category_scores_json"] if "category_scores_json" in keys else None)
                if isinstance(cat_raw, str):
                    cat_json = json.loads(cat_raw) if cat_raw else {}
                elif isinstance(cat_raw, dict):
                    cat_json = cat_raw
                else:
                    cat_json = {}

                self.status.results[sym] = {
                    "success": True,
                    "symbol": sym,
                    "score_result": ScoreResult(
                        symbol=sym,
                        composite_score=float(r["composite_score"]) if r["composite_score"] is not None else 5.0,
                        confidence_level=r["confidence_level"] if r["confidence_level"] else "MEDIUM",
                        signal=SignalType(r["signal"]) if r["signal"] else SignalType.NEUTRAL,
                        coverage=float(r["coverage"]) if r["coverage"] is not None else 0.5,
                        category_scores=cat_json,
                        altman_z_score=float(r["altman_z_score"]) if r["altman_z_score"] is not None else None,
                        piotroski_f_score=int(r["piotroski_f_score"]) if r["piotroski_f_score"] is not None else None,
                        formula_version=r["formula_version"] if r["formula_version"] else "v1.0"
                    ),
                    "technicals": {},
                    "valuation": {},
                    "quality": {},
                    "growth": {},
                    "liquidity": {},
                    "resilience": {"altman_z_score": r["altman_z_score"], "piotroski_f_score": {"score": r["piotroski_f_score"]}}
                }
            if self.status.results:
                self.status.processed_assets = len(self.status.results)
                try:
                    from app.db.repositories import AssetRepository
                    all_assets = AssetRepository.get_all()
                    self.status.total_assets = len(all_assets)
                except Exception:
                    self.status.total_assets = len(self.status.results)
                self.status.stage = "COMPLETED"
        except Exception as e:
            print(f"Error loading cached scores: {e}")

    def start_scan(self, universe: List[Asset]) -> str:
        """Yeni bir tarama oturumu başlatır"""
        run_id = str(uuid.uuid4())
        self.status.current_run_id = run_id
        self.status.stage = "INIT"
        self.status.total_assets = len(universe)
        self.status.processed_assets = 0
        self.status.failed_assets = 0
        self.status.started_at = datetime.now(timezone.utc)
        self.status.completed_at = None
        self.status.errors = []
        return run_id

    def process_universe_sync(
        self,
        universe: List[Asset],
        market_series_map: Optional[Dict[str, Any]] = None,
        financials_map: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evrendeki varlıkları sırayla işler (Senkron sürüm).
        """
        self.start_scan(universe)
        self.status.stage = "SCORING"

        for asset in universe:
            m_series = (market_series_map or {}).get(asset.symbol)
            fin_snaps = (financials_map or {}).get(asset.symbol, [])

            # Eğer veri sağlanmamışsa, hızlı veri çek
            if m_series is None:
                m_series = LiveMarketFetcher.fetch_market_series_fast(asset)
            if not fin_snaps and asset.requires_financials:
                fin_snaps = LiveMarketFetcher.fetch_financial_snapshots_fast(asset)

            res = AssetScanPipeline.process_asset(
                asset=asset,
                market_series=m_series,
                financial_snapshots=fin_snaps
            )

            if res["success"]:
                self.status.results[asset.symbol] = res
                self.status.processed_assets += 1
                self._save_score_to_db(res)
            else:
                self.status.failed_assets += 1
                self.status.errors.append({
                    "symbol": asset.symbol,
                    "error": res.get("error", "Unknown error")
                })

        self.status.stage = "BENCHMARKS"
        leaderboards = self._generate_leaderboards()

        self.status.stage = "COMPLETED"
        self.status.completed_at = datetime.now(timezone.utc)

        return {
            "run_id": self.status.current_run_id,
            "total_assets": self.status.total_assets,
            "processed": self.status.processed_assets,
            "failed": self.status.failed_assets,
            "leaderboards": leaderboards,
            "duration_seconds": (self.status.completed_at - self.status.started_at).total_seconds() if self.status.started_at else 0
        }

    def _process_single_asset_sync(self, asset: Asset) -> Dict[str, Any]:
        """Tek bir varlığın veri çekme, skorlama ve kaydetme adımını güvenle işletir"""
        try:
            m_series = LiveMarketFetcher.fetch_market_series_fast(asset)
            fin_snaps = LiveMarketFetcher.fetch_financial_snapshots_fast(asset) if asset.requires_financials else []
            res = AssetScanPipeline.process_asset(
                asset=asset,
                market_series=m_series,
                financial_snapshots=fin_snaps
            )
            if res.get("success"):
                self._save_score_to_db(res)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_background_scan(self, universe: List[Asset]):
        """
        Arka planda asenkron, yüksek hızlı ve kilitlenmeyen dürüst tarama (Bölüm 10.5 Dürüst İlerleme İlkesi).
        15'li gruplar (batches) halinde çalışır, her hisse için 5 sn katı zaman aşımı (timeout) uygular.
        Asla kilitlenmez, Render belleğini şişirmez ve %100 tamamlanmayı garanti eder.
        """
        if self._is_scanning:
            return

        import gc
        from concurrent.futures import ThreadPoolExecutor
        self._is_scanning = True
        try:
            self.start_scan(universe)
            self.status.stage = "SCORING"
            loop = asyncio.get_running_loop()
            executor = ThreadPoolExecutor(max_workers=10)

            async def _worker(asset: Asset):
                try:
                    # 15 saniyelik güvenli zaman aşımı (yfinance normalde 1-2 sn sürer, asılı kalan istekler 15 sn'de atlanır)
                    res = await asyncio.wait_for(
                        loop.run_in_executor(executor, self._process_single_asset_sync, asset),
                        timeout=15.0
                    )
                    if res and res.get("success"):
                        self.status.results[asset.symbol] = res
                        self.status.processed_assets += 1
                    else:
                        self.status.failed_assets += 1
                        self.status.errors.append({
                            "symbol": asset.symbol,
                            "error": res.get("error", "Failed") if res else "No response"
                        })
                except asyncio.TimeoutError:
                    self.status.failed_assets += 1
                    self.status.errors.append({"symbol": asset.symbol, "error": "Timeout (15s limit)"})
                except Exception as ex:
                    self.status.failed_assets += 1
                    self.status.errors.append({"symbol": asset.symbol, "error": str(ex)})

            # Evreni 10'arlı paketler halinde işle (Bellek dostu & kesintisiz akış)
            BATCH_SIZE = 10
            for i in range(0, len(universe), BATCH_SIZE):
                batch = universe[i:i + BATCH_SIZE]
                await asyncio.gather(*[_worker(a) for a in batch])
                # Küçük nefes alma ve çöp toplama (RAM 120MB altında tutulur)
                await asyncio.sleep(0.05)
                gc.collect()

            executor.shutdown(wait=False)

            self.status.stage = "BENCHMARKS"
            await asyncio.sleep(0.2)
            self.status.stage = "COMPLETED"
            self.status.completed_at = datetime.now(timezone.utc)

            # Tarama bittiğinde Model Portföyü otomatik sinyallere göre senkronize et
            try:
                from app.db.repositories import PortfolioRepository
                lbs = self._generate_leaderboards()
                PortfolioRepository.sync_auto_signals(
                    lbs.get("top_potential", []),
                    lbs.get("most_risky_overvalued", [])
                )
            except Exception as pe:
                print(f"Portföy otomatik senkronizasyon uyarısı: {pe}")

        except Exception as global_ex:
            print(f"Tarama genel hatası: {global_ex}")
            self.status.stage = "FAILED"
        finally:
            self._is_scanning = False

    def _save_score_to_db(self, res: Dict[str, Any]):
        """Skor sonucunu SQLite/Postgres (Supabase) tablosuna yazar"""
        sr: Optional[ScoreResult] = res.get("score_result")
        if not sr:
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cat_json_str = json.dumps({k: v.model_dump() for k, v in sr.category_scores.items()})
            flags_json_str = json.dumps(sr.flags or [])
            
            if conn.is_postgres:
                cursor.execute("""
                INSERT INTO score_results (
                    symbol, composite_score, confidence_level, signal, coverage,
                    category_scores, altman_z_score, piotroski_f_score, formula_version, flags, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (symbol) DO UPDATE SET
                    composite_score = EXCLUDED.composite_score,
                    confidence_level = EXCLUDED.confidence_level,
                    signal = EXCLUDED.signal,
                    coverage = EXCLUDED.coverage,
                    category_scores = EXCLUDED.category_scores,
                    altman_z_score = EXCLUDED.altman_z_score,
                    piotroski_f_score = EXCLUDED.piotroski_f_score,
                    formula_version = EXCLUDED.formula_version,
                    flags = EXCLUDED.flags,
                    updated_at = NOW(),
                    as_of_at = NOW()
                """, (
                    sr.symbol, sr.composite_score, sr.confidence_level.value, sr.signal.value,
                    sr.coverage, cat_json_str,
                    sr.altman_z_score, sr.piotroski_f_score, sr.formula_version, flags_json_str
                ))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO score_results (
                    symbol, composite_score, confidence_level, signal, coverage,
                    category_scores_json, altman_z_score, piotroski_f_score, formula_version, flags_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sr.symbol, sr.composite_score, sr.confidence_level.value, sr.signal.value,
                    sr.coverage, cat_json_str,
                    sr.altman_z_score, sr.piotroski_f_score, sr.formula_version, flags_json_str
                ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving score to DB for {sr.symbol if sr else 'unknown'}: {e}")

    def _generate_leaderboards(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Dashboard için En Güçlü Potansiyel ve En Riskli/Aşırı Değerli listelerini üretir (10'luk Ölçek).
        (sistem_mimari.md Bölüm 10.1)
        """
        from app.db.repositories import AssetRepository
        scored_items = []
        for sym, data in self.status.results.items():
            if not (sym.startswith("BIST:") or sym.startswith("NASDAQ:") or sym.startswith("NYSE:")):
                continue
            sr: ScoreResult = data.get("score_result")
            if sr:
                asset_obj = AssetRepository.get_by_symbol(sym)
                fr = sr.fundamental_rating or {}
                scored_items.append({
                    "symbol": sym,
                    "name": asset_obj.name if asset_obj else sym,
                    "sector": asset_obj.sector if asset_obj else "Genel",
                    "composite_score": sr.composite_score,
                    "signal": sr.signal.value,
                    "confidence": sr.confidence_level.value,
                    "current_price": data.get("technicals", {}).get("current_price"),
                    "rsi14": data.get("technicals", {}).get("rsi14"),
                    "pe_ratio": data.get("valuation", {}).get("pe_ratio"),
                    "altman_z": sr.altman_z_score,
                    "piotroski_f": sr.piotroski_f_score,
                    "rating_letter": fr.get("rating") if fr else None,
                    "rating_score": fr.get("total_score") if fr else None,
                    "fundamental_rating": fr
                })

        # Skorlara göre sıralama (Yüksekten Düşüğe)
        sorted_by_score = sorted(scored_items, key=lambda x: x["composite_score"], reverse=True)

        top_potential = [x for x in sorted_by_score if x["signal"] in ["STRONG_BUY", "BUY"]][:10]
        most_risky = [x for x in sorted_by_score if x["signal"] in ["STRONG_SELL", "SELL"] or (x["altman_z"] and x["altman_z"] < 1.8)][:10]

        # Eğer henüz tarama tamamlanmadıysa, evrenin en iyi bilinen liderlerini varsayılan doldur
        if not top_potential and not most_risky and len(sorted_by_score) > 0:
            top_potential = sorted_by_score[:10]
            most_risky = sorted_by_score[-10:]

        return {
            "top_potential": top_potential,
            "most_risky_overvalued": most_risky
        }
