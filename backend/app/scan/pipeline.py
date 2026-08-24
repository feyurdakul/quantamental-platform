"""
Tek Varlık Tarama ve Hesaplama Boru Hattı (sistem_mimari.md Bölüm 9)
İşlem sırası:
provider verisi alındı → teknik metrikler → finansallar → geçerlilik kapısı → türetilmiş oranlar & dayanıklılık → skor/sinyal → sonuç üretildi.
"""

import traceback
from typing import Optional, Dict, Any, List
from app.models.asset import Asset, AssetClass
from app.models.financials import FinancialSnapshot
from app.models.market_data import MarketSeries
from app.models.score import ScoreResult
from app.validation.financial_validator import FinancialValidator
from app.engine.technical import TechnicalEngine
from app.engine.fundamental import FundamentalEngine
from app.engine.resilience import ResilienceEngine
from app.engine.scorer import ScorerEngine


class AssetScanPipeline:
    """
    sistem_mimari.md Bölüm 9 Varlık Bazlı Doğru İşlem Sırası Uygulayıcısı.
    """

    @classmethod
    def process_asset(
        cls,
        asset: Asset,
        market_series: Optional[MarketSeries],
        financial_snapshots: List[FinancialSnapshot],
        previous_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Tek bir varlığı tüm hesaplama motorlarından geçirir. Hata durumunda diğer varlıkları etkilemez.
        """
        try:
            # 1. TEKNİK METRİKLER (Bölüm 5)
            technicals = {}
            if market_series and market_series.points:
                technicals = TechnicalEngine.compute_all_technicals(market_series.points)

            # 2. FİNANSAL TABLOLAR VE GEÇERLİLİK KAPISI (Bölüm 4.1 & 6)
            valuation = {}
            quality = {}
            growth = {}
            liquidity = {}
            resilience = {}

            if asset.requires_financials and financial_snapshots:
                # Geçerli snapshot filtrelemesi
                valid_snaps = [s for s in financial_snapshots if FinancialValidator.validate_snapshot(s)]
                sorted_snaps = sorted(valid_snaps, key=lambda s: s.period_end)

                if sorted_snaps:
                    curr_snap = sorted_snaps[-1]
                    prev_snap = sorted_snaps[-2] if len(sorted_snaps) >= 2 else None

                    # Güncel piyasa fiyatını snapshot'a enjekte et
                    if technicals.get("current_price"):
                        curr_snap.market_context.current_price = technicals.get("current_price")

                    # Oran hesapları
                    valuation = FundamentalEngine.calculate_valuation_metrics(curr_snap)
                    quality = FundamentalEngine.calculate_quality_metrics(curr_snap, prev_snap)
                    growth = FundamentalEngine.calculate_growth_metrics(sorted_snaps)
                    liquidity = FundamentalEngine.calculate_liquidity_and_leverage_metrics(curr_snap)

                    # Dayanıklılık modelleri (Bölüm 7)
                    is_bank = asset.is_financial_institution()
                    altman_z = ResilienceEngine.calculate_altman_z_score(curr_snap, is_bank_or_financial=is_bank)
                    piotroski_f = ResilienceEngine.calculate_piotroski_f_score(sorted_snaps)
                    
                    resilience = {
                        "altman_z_score": altman_z,
                        "piotroski_f_score": piotroski_f
                    }

            # 3. SKOR, SİNYAL VE GÜVEN SEVİYESİ (Bölüm 8)
            score_result = ScorerEngine.score_asset(
                asset=asset,
                technicals=technicals,
                valuation=valuation,
                quality=quality,
                growth=growth,
                liquidity=liquidity,
                resilience=resilience,
                previous_score=previous_score
            )

            return {
                "success": True,
                "symbol": asset.symbol,
                "score_result": score_result,
                "technicals": technicals,
                "valuation": valuation,
                "quality": quality,
                "growth": growth,
                "liquidity": liquidity,
                "resilience": resilience,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "symbol": asset.symbol,
                "score_result": None,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
