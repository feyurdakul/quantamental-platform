"""
St. Louis Fed (FRED / ALFRED) Makroekonomik Veri Sağlayıcı Adaptörü (fredapi)
Para politikası, getiri eğrisi, likidite ve ALFRED Point-in-Time tarihsel revizyonları (sistem_mimari.md Bölüm 11 & 12).
"""

from typing import Optional, Dict, Any
import pandas as pd
from app.providers.base import BaseProvider


class FredProvider(BaseProvider):
    """
    fredapi sarmalayıcısı ve makro rejim motoru adaptörü.
    """

    # Temel Makro Gösterge Sepeti
    CORE_MACRO_SERIES = {
        "10Y_Treasury": "DGS10",          # ABD 10 Yıllık Tahvil Faizi
        "2Y_Treasury": "DGS2",            # ABD 2 Yıllık Tahvil Faizi
        "Yield_Spread_10Y_2Y": "T10Y2Y",  # Getiri Eğrisi (Resesyon Öncüsü)
        "Fed_Funds_Rate": "FEDFUNDS",     # Fed Politika Faizi
        "Fed_Total_Assets": "WALCL",      # Fed Bilanço Büyüklüğü (Milyon USD)
        "US_M2_Money_Supply": "M2SL",     # M2 Para Arzı
        "US_CPI": "CPIAUCSL",             # ABD TÜFE Enflasyonu
        "US_GDP": "GDP",                  # ABD GSYİH
        "US_Unemployment": "UNRATE",      # ABD İşsizlik Oranı
        "VIX_Index": "VIXCLS"             # Volatilite / Korku Endeksi
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._fred_client = None

    @property
    def provider_name(self) -> str:
        return "fredapi"

    @property
    def client(self):
        if self._fred_client is None:
            from fredapi import Fred
            self._fred_client = Fred(api_key=self.api_key)
        return self._fred_client

    def fetch_macro_series(self, series_id: str, limit: int = 100) -> Optional[pd.Series]:
        """
        Tek bir makro seriyi çeker.
        """
        try:
            return self.client.get_series(series_id)
        except Exception:
            return None

    def fetch_all_core_macro(self) -> Dict[str, Any]:
        """
        Tüm çekirdek makro göstergeleri çeker ve güncel makro rejim durumunu döndürür.
        """
        macro_state: Dict[str, Any] = {}
        for name, sid in self.CORE_MACRO_SERIES.items():
            try:
                s = self.client.get_series(sid)
                if s is not None and not s.empty:
                    last_val = s.dropna().iloc[-1]
                    last_date = s.dropna().index[-1].strftime("%Y-%m-%d")
                    macro_state[name] = {
                        "series_id": sid,
                        "latest_value": float(last_val),
                        "latest_date": last_date
                    }
            except Exception:
                continue

        # Makro Rejim Teşhisi (sistem_mimari.md Bölüm 11)
        spread = macro_state.get("Yield_Spread_10Y_2Y", {}).get("latest_value")
        vix = macro_state.get("VIX_Index", {}).get("latest_value")
        
        regime = "NORMAL"
        if spread is not None and spread < 0:
            regime = "INVERTED_YIELD_CURVE_RECESSION_RISK"
        elif vix is not None and vix > 25.0:
            regime = "HIGH_VOLATILITY_RISK_OFF"

        macro_state["macro_regime"] = regime
        return macro_state

    def fetch_point_in_time_vintage(self, series_id: str, vintage_date: str) -> Optional[pd.Series]:
        """
        ALFRED Point-in-Time Revizyon Verisi:
        Belirtilen geçmiş tarihte (vintage_date) piyasanın GERÇEKTE bildiği revize edilmemiş veriyi çeker.
        (sistem_mimari.md Bölüm 11 & 12 - Look-ahead bias engelleme)
        """
        try:
            return self.client.get_series_as_of_date(series_id, vintage_date)
        except Exception:
            return None
