"""
6-Faktörlü Temel Derecelendirme Modeli (Fundamental Rating Engine)
6 Metrik x 5 Puan = 6 - 30 Puan Aralığı ve S, A, B, C, D Harf Notu Sistemi
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class FundamentalRating(BaseModel):
    """6-Faktörlü Temel Derecelendirme Çıktısı"""
    total_score: int = Field(..., description="Toplam puan (6 - 30)")
    max_score: int = Field(30, description="Maksimum puan")
    rating: str = Field(..., description="Harf Notu: S, A, B, C, D")
    recommendation: str = Field(..., description="Tavsiye: Strong Buy, Buy, Neutral, Sell, Strong Sell")
    is_applicable: bool = Field(True, description="Finansal veri uygulanabilir mi?")
    metric_breakdown: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="6 metriğin bireysel puanları")


class FundamentalRatingEngine:
    """
    Kullanıcı Tanımlı 6-Faktörlü Temel Derecelendirme Motoru
    
    Metrikler:
    1. DCF / FCF Marjı: [0.25, 0.10, 0.00, -0.15] (Yüksek iyi)
    2. ROE: [0.20, 0.10, 0.05, 0.00] (Yüksek iyi)
    3. ROA: [0.10, 0.05, 0.02, 0.00] (Yüksek iyi)
    4. Debt to Equity: [0.2, 0.5, 1.0, 2.0] (Düşük iyi)
    5. P/E (F/K): [15, 25, 40, 999] (Düşük iyi, Negatifse doğrudan 1 puan)
    6. P/B (PD/DD): [1.5, 3.0, 5.0, 10.0] (Düşük iyi)
    """

    @classmethod
    def score_high_is_good(cls, val: Optional[float], thresholds: list) -> int:
        """Yüksek olması iyi olan metrikler için (DCF, ROE, ROA) 1-5 puan"""
        if val is None:
            return 3  # Nötr varsayılan
        
        t1, t2, t3, t4 = thresholds
        if val >= t1:
            return 5  # Strong Buy
        elif val >= t2:
            return 4  # Buy
        elif val >= t3:
            return 3  # Neutral
        elif val >= t4:
            return 2  # Sell
        else:
            return 1  # Strong Sell

    @classmethod
    def score_low_is_good(cls, val: Optional[float], thresholds: list, is_pe: bool = False) -> int:
        """Düşük olması iyi olan metrikler için (D/E, P/E, P/B) 1-5 puan"""
        if val is None:
            return 3  # Nötr varsayılan
        
        # F/K için özel kural: Negatifse (zarar) doğrudan 1 puan
        if is_pe and val < 0:
            return 1

        t1, t2, t3, t4 = thresholds
        if val <= t1:
            return 5  # Strong Buy
        elif val <= t2:
            return 4  # Buy
        elif val <= t3:
            return 3  # Neutral
        elif val <= t4:
            return 2  # Sell
        else:
            return 1  # Strong Sell

    @classmethod
    def compute_rating(
        cls,
        valuation: Dict[str, Any],
        quality: Dict[str, Any],
        liquidity: Dict[str, Any],
        is_financial_asset: bool = True
    ) -> FundamentalRating:
        """
        6 metriği puanlar ve toplam 6-30 puan aralığında harf notu üretir.
        """
        if not is_financial_asset:
            return FundamentalRating(
                total_score=0,
                max_score=30,
                rating="—",
                recommendation="Uygulanamaz",
                is_applicable=False,
                metric_breakdown={}
            )

        # 1. DCF / FCF Marjı veya FCF Verimi
        # FCF Verimi veya FCF / Revenue
        fcf_yield = valuation.get("fcf_yield")
        fcf_margin = quality.get("fcf_margin", fcf_yield if fcf_yield is not None else 0.05)
        dcf_pts = cls.score_high_is_good(fcf_margin, [0.25, 0.10, 0.00, -0.15])

        # 2. ROE (Özkaynak Kârlılığı)
        roe = quality.get("roe")
        roe_pts = cls.score_high_is_good(roe, [0.20, 0.10, 0.05, 0.00])

        # 3. ROA (Aktif Kârlılığı)
        roa = quality.get("roa")
        roa_pts = cls.score_high_is_good(roa, [0.10, 0.05, 0.02, 0.00])

        # 4. Debt to Equity (Borç / Özkaynak)
        de = liquidity.get("net_debt_to_equity", liquidity.get("debt_to_equity"))
        de_pts = cls.score_low_is_good(de, [0.2, 0.5, 1.0, 2.0])

        # 5. Price to Earnings (F/K)
        pe = valuation.get("pe_ratio")
        pe_pts = cls.score_low_is_good(pe, [15, 25, 40, 999], is_pe=True)

        # 6. Price to Book (PD/DD)
        pb = valuation.get("pb_ratio")
        pb_pts = cls.score_low_is_good(pb, [1.5, 3.0, 5.0, 10.0])

        total_score = dcf_pts + roe_pts + roa_pts + de_pts + pe_pts + pb_pts

        # Harf Notu ve Tavsiye Eşikleri (6 - 30 Puan)
        if total_score >= 25:
            rating = "S"
            recommendation = "Strong Buy"
        elif total_score >= 19:
            rating = "A"
            recommendation = "Buy"
        elif total_score >= 13:
            rating = "B"
            recommendation = "Neutral"
        elif total_score >= 9:
            rating = "C"
            recommendation = "Sell"
        else:
            rating = "D"
            recommendation = "Strong Sell"

        metric_breakdown = {
            "dcf_margin": {"value": fcf_margin, "points": dcf_pts, "label": "DCF / FCF Marjı"},
            "roe": {"value": roe, "points": roe_pts, "label": "Özkaynak Kârlılığı (ROE)"},
            "roa": {"value": roa, "points": roa_pts, "label": "Aktif Kârlılığı (ROA)"},
            "debt_to_equity": {"value": de, "points": de_pts, "label": "Borç / Özkaynak (D/E)"},
            "pe_ratio": {"value": pe, "points": pe_pts, "label": "F/K Oranı (P/E)"},
            "pb_ratio": {"value": pb, "points": pb_pts, "label": "PD/DD Oranı (P/B)"},
        }

        return FundamentalRating(
            total_score=total_score,
            max_score=30,
            rating=rating,
            recommendation=recommendation,
            is_applicable=True,
            metric_breakdown=metric_breakdown
        )
