"""
Veri Kalitesi, Teşhis ve Uyarı Bayrakları (sistem_mimari.md Bölüm 4)
"""

from enum import Enum
from typing import Optional, List
from app.models.asset import AssetClass


class QualityFlag(str, Enum):
    VALID = "VALID"
    MISSING = "MISSING"                                   # Kaynak alanı yok
    INVALID = "INVALID"                                   # Matematiksel olarak anlamsız/bozuk değer
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"               # Trend veya model için yeterli dönem yok
    STRUCTURAL_NA = "STRUCTURAL_NA"                       # İlgili varlık sınıfına yapısal olarak uygulanamaz
    BASE_EFFECT_WARNING = "BASE_EFFECT_WARNING"           # Negatiften pozitife / sıfıra yakın büyüme yanıltması (Bölüm 6.3)
    HIGH_TOTAL_LIABILITIES = "HIGH_TOTAL_LIABILITIES"     # liabilities_to_equity > 5.0 teşhis bayrağı (Bölüm 6.5)
    COMPARABILITY_LIMITED = "COMPARABILITY_LIMITED"       # BIST TMS-29 enflasyon muhasebesi karşılaştırılabilirlik sınırı (Bölüm 4.3)
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"               # Pay ve payda para birimi uyuşmazlığı (Bölüm 4.3)
    NEGATIVE_EARNINGS = "NEGATIVE_EARNINGS"               # Negatif kâr/EBITDA sebebiyle değerleme geçersiz (Bölüm 6.1)


class QualityChecker:
    """
    sistem_mimari.md Bölüm 4 Veri Kalitesi ve Güvenlik Kuralları Denetleyicisi.
    """

    @staticmethod
    def is_structurally_applicable(metric_key: str, asset_class: AssetClass, is_bank_or_insurance: bool = False) -> bool:
        """
        Bir metriğin ilgili varlık sınıfına yapısal olarak uygulanıp uygulanamayacağını belirler.
        (sistem_mimari.md Bölüm 2 & 8.2)
        """
        # Şirket finansallarına dayanan tüm metrikler ETF/Kripto/FX/Emtia/Endeks için structural_na'dır
        non_financial_assets = [
            AssetClass.ETF, AssetClass.CRYPTO, AssetClass.FOREX,
            AssetClass.COMMODITY, AssetClass.INDEX
        ]
        
        financial_metrics = [
            "pe_ratio", "pb_ratio", "ev_ebitda", "fcf_yield", "earnings_yield",
            "roe", "roa", "roic", "operating_margin", "net_margin", "gross_margin",
            "revenue_growth", "net_income_growth", "eps_growth", "fcf_growth",
            "current_ratio", "quick_ratio", "net_working_capital",
            "net_debt_to_equity", "interest_coverage", "cash_conversion_cycle",
            "altman_z_score", "piotroski_f_score"
        ]

        if asset_class in non_financial_assets and metric_key in financial_metrics:
            return False

        # Bankalar ve Sigortalar için sanayi metrikleri structural_na'dır (Bölüm 6.4, 6.6, 6.7, 7.1)
        if is_bank_or_insurance:
            bank_excluded_metrics = [
                "current_ratio", "quick_ratio", "net_working_capital",
                "interest_coverage", "cash_conversion_cycle",
                "altman_z_score", "ev_ebitda", "gross_margin", "operating_margin"
            ]
            if metric_key in bank_excluded_metrics:
                return False

        return True

    @staticmethod
    def check_currency_consistency(curr1: str, curr2: str) -> bool:
        """
        Pay ve payda para birimlerinin tutarlılığını doğrular (sistem_mimari.md Bölüm 4.3).
        Farklı para birimlerinin doğrudan bölünmesi kesinlikle yasaktır.
        """
        return curr1.strip().upper() == curr2.strip().upper()
