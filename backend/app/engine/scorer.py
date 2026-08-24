"""
Bütünleşik Skor ve Sinyal Motoru (sistem_mimari.md Bölüm 8)
Kategori ağırlıkları, puan bantları, varlık şablonları, güven seviyesi ve histerezis.
"""

from typing import Dict, Optional, List, Any
from app.models.asset import Asset, AssetClass
from app.models.score import (
    ScoreResult,
    CategoryScoreDetail,
    MetricScoreDetail,
    ConfidenceLevel,
    SignalType
)


class ScorerEngine:
    """
    sistem_mimari.md Bölüm 8 Spesifikasyonuna uygun 5 Kategorili Skor Motoru.
    """

    # 1. Puanlama Bantları (2.0 - 10.0 Puan)
    @staticmethod
    def score_pe_ratio(val: Optional[float]) -> tuple[Optional[float], str]:
        if val is None or val <= 0:
            return None, "missing/negative"
        if val <= 8.0:
            return 10.0, "Çok Ucuz (≤8x)"
        elif val <= 14.0:
            return 8.0, "Makul (8-14x)"
        elif val <= 22.0:
            return 6.0, "Piyasa Ortalaması (14-22x)"
        elif val <= 35.0:
            return 4.0, "Pahalı (22-35x)"
        else:
            return 2.0, "Aşırı Değerli (>35x)"

    @staticmethod
    def score_pb_ratio(val: Optional[float]) -> tuple[Optional[float], str]:
        if val is None or val <= 0:
            return None, "missing/negative"
        if val <= 1.2:
            return 10.0, "Defter Değerine Yakın (≤1.2x)"
        elif val <= 2.5:
            return 8.0, "Sağlıklı (1.2-2.5x)"
        elif val <= 5.0:
            return 6.0, "Normal (2.5-5.0x)"
        elif val <= 10.0:
            return 4.0, "Yüksek (5-10x)"
        else:
            return 2.0, "Aşırı Yüksek (>10x)"

    @staticmethod
    def score_roe(val: Optional[float]) -> tuple[Optional[float], str]:
        if val is None:
            return None, "missing"
        if val >= 0.30:
            return 10.0, "Kuvvetli ROE (≥%30)"
        elif val >= 0.20:
            return 8.0, "İyi ROE (%20-%30)"
        elif val >= 0.10:
            return 6.0, "Ortalama ROE (%10-%20)"
        elif val >= 0.0:
            return 4.0, "Zayıf ROE (%0-%10)"
        else:
            return 2.0, "Negatif Kârlılık (<%0)"

    @staticmethod
    def score_operating_margin(val: Optional[float]) -> tuple[Optional[float], str]:
        if val is None:
            return None, "missing"
        if val >= 0.25:
            return 10.0, "Mükemmel Marj (≥%25)"
        elif val >= 0.15:
            return 8.0, "Güçlü Marj (%15-%25)"
        elif val >= 0.08:
            return 6.0, "Normal Marj (%8-%15)"
        elif val >= 0.0:
            return 4.0, "Düşük Marj (%0-%8)"
        else:
            return 2.0, "Faaliyet Zararı (<%0)"

    @staticmethod
    def score_net_debt_to_equity(val: Optional[float], gross_debt_to_equity: Optional[float] = None) -> tuple[Optional[float], str]:
        """
        Net Borç / Özsermaye Puanı (sistem_mimari.md Bölüm 6.5)
        Brüt borç koruması: total_debt / equity > 4.0 ise puan en fazla 4.0 olabilir.
        """
        if val is None:
            return None, "missing"
        
        score = 2.0
        note = ""
        if val <= 0.25:
            score = 10.0
            note = "Çok Düşük Borç / Net Nakitte (≤0.25x)"
        elif val <= 0.50:
            score = 8.0
            note = "Düşük Kaldıraç (0.25-0.50x)"
        elif val <= 1.00:
            score = 6.0
            note = "Yönetilebilir Borç (0.50-1.00x)"
        elif val <= 2.00:
            score = 4.0
            note = "Yüksek Borç (1.00-2.00x)"
        else:
            score = 2.0
            note = "Kritik Borçluluk (≥2.00x)"

        # Brüt borç koruması
        if gross_debt_to_equity and gross_debt_to_equity > 4.0:
            score = min(score, 4.0)
            note += " [Brüt Borç Koruması Devrede]"

        return score, note

    @staticmethod
    def score_current_ratio(val: Optional[float]) -> tuple[Optional[float], str]:
        if val is None:
            return None, "missing"
        if val >= 2.0:
            return 10.0, "Kuvvetli Likidite (≥2.0x)"
        elif val >= 1.5:
            return 8.0, "Sağlıklı (1.5-2.0x)"
        elif val >= 1.0:
            return 6.0, "Yeterli (1.0-1.5x)"
        elif val >= 0.7:
            return 4.0, "Dar Likidite (0.7-1.0x)"
        else:
            return 2.0, "Likit Kriz Riski (<0.7x)"

    @staticmethod
    def score_revenue_growth(val: Optional[float]) -> tuple[Optional[float], str]:
        if val is None:
            return None, "missing"
        if val >= 0.35:
            return 10.0, "Yüksek Büyüme (≥%35)"
        elif val >= 0.20:
            return 8.0, "Güçlü Büyüme (%20-%35)"
        elif val >= 0.08:
            return 6.0, "İstikrarlı (%8-%20)"
        elif val >= 0.0:
            return 4.0, "Durgun Büyüme (%0-%8)"
        else:
            return 2.0, "Gelirde Küçülme (<%0)"

    @staticmethod
    def score_rsi(val: Optional[float]) -> tuple[Optional[float], str]:
        if val is None:
            return None, "missing"
        if 40.0 <= val <= 65.0:
            return 10.0, "Sağlıklı Trend Bölgesi (40-65)"
        elif (30.0 <= val < 40.0) or (65.0 < val <= 75.0):
            return 8.0, "Momentum / Toparlanma Bölgesi"
        elif 20.0 <= val < 30.0:
            return 6.0, "Aşırı Satım (Potansiyel Tepki)"
        elif 75.0 < val <= 85.0:
            return 4.0, "Aşırı Alım (Düzeltme Riski)"
        else:
            return 2.0, "Ekstrem RSI Seviyesi (<20 veya >85)"

    @staticmethod
    def score_trend_regime(trend_regime: str, price_vs_sma200: Optional[float]) -> tuple[Optional[float], str]:
        if trend_regime == "POSITIVE":
            if price_vs_sma200 and price_vs_sma200 > 0:
                return 10.0, "Boğa Piyasası / Güçlü Trend (SMA50 > SMA200 & Fiyat > SMA200)"
            return 8.0, "Pozitif Trend Eğilimi"
        elif trend_regime == "NEGATIVE":
            if price_vs_sma200 and price_vs_sma200 < 0:
                return 2.0, "Ayı Piyasası / Zayıf Trend (SMA50 < SMA200 & Fiyat < SMA200)"
            return 4.0, "Negatif Trend Eğilimi"
        return 6.0, "Nötr / Kararsız Görünüm"

    @classmethod
    def score_asset(
        cls,
        asset: Asset,
        technicals: Dict[str, Any],
        valuation: Dict[str, Any],
        quality: Dict[str, Any],
        growth: Dict[str, Any],
        liquidity: Dict[str, Any],
        resilience: Dict[str, Any],
        previous_score: Optional[float] = None
    ) -> ScoreResult:
        """
        Tüm metrikleri varlık şablonuna göre puanlar, güven seviyesi ve sinyal üretir.
        """
        is_bank = asset.is_financial_institution()
        asset_class = asset.asset_class

        categories: Dict[str, CategoryScoreDetail] = {}

        # 1. DEĞERLEME KATEGORİSİ (Valuation)
        val_metrics: List[MetricScoreDetail] = []
        if asset_class in [AssetClass.BIST_STOCK, AssetClass.US_STOCK, AssetClass.BANK_STOCK]:
            # P/E
            pe_s, pe_note = cls.score_pe_ratio(valuation.get("pe_ratio"))
            val_metrics.append(MetricScoreDetail(
                metric_key="pe_ratio", display_name="Fiyat / Kazanç (F/K)",
                raw_value=valuation.get("pe_ratio"), formatted_value=f"{valuation.get('pe_ratio')}x" if valuation.get("pe_ratio") else None,
                score=pe_s, weight=1.5, is_valid=(pe_s is not None), status="valid" if pe_s else "missing", notes=pe_note
            ))
            # P/B
            pb_s, pb_note = cls.score_pb_ratio(valuation.get("pb_ratio"))
            val_metrics.append(MetricScoreDetail(
                metric_key="pb_ratio", display_name="Piyasa Değeri / Defter Değeri (PD/DD)",
                raw_value=valuation.get("pb_ratio"), formatted_value=f"{valuation.get('pb_ratio')}x" if valuation.get("pb_ratio") else None,
                score=pb_s, weight=1.0 if not is_bank else 2.0, is_valid=(pb_s is not None), status="valid" if pb_s else "missing", notes=pb_note
            ))

        val_applicable = len(val_metrics) > 0
        val_valid_w = sum(m.weight for m in val_metrics if m.is_valid)
        val_total_w = sum(m.weight for m in val_metrics)
        val_score = sum(m.score * m.weight for m in val_metrics if m.is_valid and m.score) / val_valid_w if val_valid_w > 0 else None
        
        categories["valuation"] = CategoryScoreDetail(
            category_key="valuation", category_name="Değerleme",
            category_score=round(val_score, 2) if val_score else None,
            theoretical_weight=0.25 if val_applicable else 0.0,
            effective_weight=0.25 if val_applicable else 0.0,
            is_applicable=val_applicable, metrics=val_metrics
        )

        # 2. KALİTE VE KÂRLILIK KATEGORİSİ (Quality)
        qual_metrics: List[MetricScoreDetail] = []
        if asset_class in [AssetClass.BIST_STOCK, AssetClass.US_STOCK, AssetClass.BANK_STOCK]:
            # ROE
            roe_s, roe_note = cls.score_roe(quality.get("roe"))
            qual_metrics.append(MetricScoreDetail(
                metric_key="roe", display_name="Özsermaye Kârlılığı (ROE)",
                raw_value=quality.get("roe"), formatted_value=f"%{round(quality.get('roe')*100, 1)}" if quality.get("roe") else None,
                score=roe_s, weight=1.5, is_valid=(roe_s is not None), status="valid" if roe_s else "missing", notes=roe_note
            ))
            # Faaliyet Marjı (Bankalarda yok)
            if not is_bank:
                om_s, om_note = cls.score_operating_margin(quality.get("operating_margin"))
                qual_metrics.append(MetricScoreDetail(
                    metric_key="operating_margin", display_name="Faaliyet Kâr Marjı",
                    raw_value=quality.get("operating_margin"), formatted_value=f"%{round(quality.get('operating_margin')*100, 1)}" if quality.get("operating_margin") else None,
                    score=om_s, weight=1.2, is_valid=(om_s is not None), status="valid" if om_s else "missing", notes=om_note
                ))

        qual_applicable = len(qual_metrics) > 0
        qual_valid_w = sum(m.weight for m in qual_metrics if m.is_valid)
        qual_total_w = sum(m.weight for m in qual_metrics)
        qual_score = sum(m.score * m.weight for m in qual_metrics if m.is_valid and m.score) / qual_valid_w if qual_valid_w > 0 else None

        categories["quality"] = CategoryScoreDetail(
            category_key="quality", category_name="Kalite & Kârlılık",
            category_score=round(qual_score, 2) if qual_score else None,
            theoretical_weight=0.20 if qual_applicable else 0.0,
            effective_weight=0.20 if qual_applicable else 0.0,
            is_applicable=qual_applicable, metrics=qual_metrics
        )

        # 3. FİNANSAL DAYANIKLILIK KATEGORİSİ (Resilience)
        res_metrics: List[MetricScoreDetail] = []
        if asset_class in [AssetClass.BIST_STOCK, AssetClass.US_STOCK] and not is_bank:
            # Net Borç / Özsermaye
            nde_s, nde_note = cls.score_net_debt_to_equity(
                liquidity.get("net_debt_to_equity"),
                liquidity.get("gross_debt_to_equity")
            )
            res_metrics.append(MetricScoreDetail(
                metric_key="net_debt_to_equity", display_name="Net Borç / Özsermaye",
                raw_value=liquidity.get("net_debt_to_equity"), formatted_value=f"{liquidity.get('net_debt_to_equity')}x" if liquidity.get("net_debt_to_equity") is not None else None,
                score=nde_s, weight=1.5, is_valid=(nde_s is not None), status="valid" if nde_s else "missing", notes=nde_note
            ))
            # Cari Oran
            cr_s, cr_note = cls.score_current_ratio(liquidity.get("current_ratio"))
            res_metrics.append(MetricScoreDetail(
                metric_key="current_ratio", display_name="Cari Oran",
                raw_value=liquidity.get("current_ratio"), formatted_value=f"{liquidity.get('current_ratio')}x" if liquidity.get("current_ratio") else None,
                score=cr_s, weight=1.0, is_valid=(cr_s is not None), status="valid" if cr_s else "missing", notes=cr_note
            ))

        res_applicable = len(res_metrics) > 0
        res_valid_w = sum(m.weight for m in res_metrics if m.is_valid)
        res_total_w = sum(m.weight for m in res_metrics)
        res_score = sum(m.score * m.weight for m in res_metrics if m.is_valid and m.score) / res_valid_w if res_valid_w > 0 else None

        categories["resilience"] = CategoryScoreDetail(
            category_key="resilience", category_name="Finansal Dayanıklılık",
            category_score=round(res_score, 2) if res_score else None,
            theoretical_weight=0.20 if res_applicable else 0.0,
            effective_weight=0.20 if res_applicable else 0.0,
            is_applicable=res_applicable, metrics=res_metrics
        )

        # 4. BÜYÜME KATEGORİSİ (Growth)
        grw_metrics: List[MetricScoreDetail] = []
        if asset_class in [AssetClass.BIST_STOCK, AssetClass.US_STOCK, AssetClass.BANK_STOCK]:
            rev_g_s, rev_g_note = cls.score_revenue_growth(growth.get("revenue_growth"))
            grw_metrics.append(MetricScoreDetail(
                metric_key="revenue_growth", display_name="Yıllık Gelir Büyümesi",
                raw_value=growth.get("revenue_growth"), formatted_value=f"%{round(growth.get('revenue_growth')*100, 1)}" if growth.get("revenue_growth") is not None else None,
                score=rev_g_s, weight=1.5, is_valid=(rev_g_s is not None), status="valid" if rev_g_s else "missing", notes=rev_g_note
            ))

        grw_applicable = len(grw_metrics) > 0
        grw_valid_w = sum(m.weight for m in grw_metrics if m.is_valid)
        grw_total_w = sum(m.weight for m in grw_metrics)
        grw_score = sum(m.score * m.weight for m in grw_metrics if m.is_valid and m.score) / grw_valid_w if grw_valid_w > 0 else None

        categories["growth"] = CategoryScoreDetail(
            category_key="growth", category_name="Büyüme",
            category_score=round(grw_score, 2) if grw_score else None,
            theoretical_weight=0.15 if grw_applicable else 0.0,
            effective_weight=0.15 if grw_applicable else 0.0,
            is_applicable=grw_applicable, metrics=grw_metrics
        )

        # 5. TEKNİK GÖRÜNÜM KATEGORİSİ (Technical) — Tüm varlık sınıflarına uygulanır
        tech_metrics: List[MetricScoreDetail] = []
        rsi_s, rsi_note = cls.score_rsi(technicals.get("rsi14"))
        tech_metrics.append(MetricScoreDetail(
            metric_key="rsi14", display_name="RSI (14)",
            raw_value=technicals.get("rsi14"), formatted_value=str(technicals.get("rsi14")),
            score=rsi_s, weight=1.0, is_valid=(rsi_s is not None), status="valid" if rsi_s else "missing", notes=rsi_note
        ))

        trend_s, trend_note = cls.score_trend_regime(
            technicals.get("trend_regime", "NEUTRAL"),
            technicals.get("price_vs_sma200")
        )
        tech_metrics.append(MetricScoreDetail(
            metric_key="trend_regime", display_name="Trend Rejimi (SMA50 vs SMA200)",
            raw_value=technicals.get("price_vs_sma200"), formatted_value=technicals.get("trend_regime"),
            score=trend_s, weight=1.5, is_valid=(trend_s is not None), status="valid" if trend_s else "missing", notes=trend_note
        ))

        tech_applicable = True
        tech_valid_w = sum(m.weight for m in tech_metrics if m.is_valid)
        tech_total_w = sum(m.weight for m in tech_metrics)
        tech_score = sum(m.score * m.weight for m in tech_metrics if m.is_valid and m.score) / tech_valid_w if tech_valid_w > 0 else None

        # ETF / Kripto / FX için teknik ağırlık %100'dür (Bölüm 8.2)
        tech_theoretical_w = 0.20 if asset_class in [AssetClass.BIST_STOCK, AssetClass.US_STOCK, AssetClass.BANK_STOCK] else 1.00
        
        categories["technical"] = CategoryScoreDetail(
            category_key="technical", category_name="Teknik Görünüm",
            category_score=round(tech_score, 2) if tech_score else None,
            theoretical_weight=tech_theoretical_w,
            effective_weight=tech_theoretical_w,
            is_applicable=tech_applicable, metrics=tech_metrics
        )

        # --- BİLEŞİK SKOR VE ETKİN AĞIRLIK HESAPLAMA ---
        # composite_score = Σ(category_score × category_weight) / Σ(effective_category_weight)
        applicable_categories = [c for c in categories.values() if c.is_applicable and c.category_score is not None]
        total_effective_weight = sum(c.effective_weight for c in applicable_categories)
        total_theoretical_weight = sum(c.theoretical_weight for c in categories.values() if c.is_applicable)

        if total_effective_weight > 0:
            raw_composite = sum(c.category_score * c.effective_weight for c in applicable_categories) / total_effective_weight
            raw_composite = round(raw_composite, 2)
        else:
            raw_composite = 6.0 # 10 üzerinden nötr taban skor

        # Kapsama Oranı (Coverage) -> Güven Seviyesi (Bölüm 8.3)
        coverage = (total_effective_weight / total_theoretical_weight) if total_theoretical_weight > 0 else 0.0
        coverage = round(coverage, 4)

        if coverage >= 0.75:
            confidence = ConfidenceLevel.HIGH
        elif coverage >= 0.40:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW

        # Histerezis Kuralı (Bölüm 8.5): 10'luk ölçekte 0.40 puan filtreleme
        final_score = raw_composite
        hysteresis_applied = False
        if previous_score is not None:
            score_diff = abs(raw_composite - previous_score)
            if score_diff < 0.40:
                final_score = previous_score # Küçük dalgalanmaları filtrele
                hysteresis_applied = True

        # Sinyal Üretimi (Bölüm 8.4): 10'luk Ölçek + Güven Seviyesi
        signal = SignalType.HOLD
        if confidence == ConfidenceLevel.HIGH:
            if final_score >= 8.40:
                signal = SignalType.STRONG_BUY
            elif final_score >= 7.20:
                signal = SignalType.BUY
            elif final_score >= 5.20:
                signal = SignalType.HOLD
            elif final_score >= 3.60:
                signal = SignalType.SELL
            else:
                signal = SignalType.STRONG_SELL
        elif confidence == ConfidenceLevel.MEDIUM:
            if final_score >= 7.60:
                signal = SignalType.BUY
            elif final_score >= 4.80:
                signal = SignalType.WATCH
            else:
                signal = SignalType.SELL
        else: # LOW Confidence
            signal = SignalType.WATCH

        # Ek Bayraklar
        flags = []
        if growth.get("base_effect_warning"):
            flags.append("BASE_EFFECT_WARNING")
        if liquidity.get("flags"):
            flags.extend(liquidity.get("flags"))

        return ScoreResult(
            symbol=asset.symbol,
            composite_score=final_score,
            confidence_level=confidence,
            signal=signal,
            coverage=coverage,
            category_scores=categories,
            altman_z_score=resilience.get("altman_z_score"),
            piotroski_f_score=resilience.get("piotroski_f_score", {}).get("score") if isinstance(resilience.get("piotroski_f_score"), dict) else None,
            raw_score_before_hysteresis=raw_composite,
            hysteresis_applied=hysteresis_applied,
            formula_version="1.0.0",
            flags=flags
        )
