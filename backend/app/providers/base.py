"""
Soyut Veri Sağlayıcı Arayüzü (sistem_mimari.md Bölüm 11)
Uygulama sağlayıcıya değil, kanonik veri sözleşmesine bağımlıdır.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.models.market_data import MarketSeries, MarketQuote
from app.models.financials import FinancialSnapshot
from app.models.analyst import AnalystEstimates


class BaseProvider(ABC):
    """
    Tüm veri sağlayıcı adaptörlerinin türeyeceği temel soyut sınıf.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Sağlayıcı adı (örn: isyatirimhisse, yfinance, FMP, Finnhub, GoogleFinance, TradingView, fredapi)"""
        pass

    async def fetch_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Anlık kotasyon / son fiyat çekme"""
        return None

    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1D", lookback_days: int = 300) -> Optional[MarketSeries]:
        """Tarihsel veya canlı OHLCV serisi çekme"""
        return None

    async def fetch_financials(self, symbol: str, years: int = 3, is_usd: bool = False) -> List[FinancialSnapshot]:
        """Finansal tablo snapshot'larını çekme"""
        return []

    async def fetch_analyst_estimates(self, symbol: str) -> Optional[AnalystEstimates]:
        """Analist hedef fiyat ve tahminlerini çekme"""
        return None
