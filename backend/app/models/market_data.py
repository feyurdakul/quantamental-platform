"""
Kanonik Piyasa ve OHLCV Veri Modelleri (sistem_mimari.md Bölüm 3.2)
"""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field


class OHLCVPoint(BaseModel):
    """
    Tek bir zaman dilimine ait kanonik OHLCV veri noktası.
    """
    timestamp: datetime = Field(..., description="Mum zaman damgası (UTC)")
    open: float = Field(..., description="Açılış fiyatı")
    high: float = Field(..., description="En yüksek fiyat")
    low: float = Field(..., description="En düşük fiyat")
    close: float = Field(..., description="Kapanış fiyatı")
    adjusted_close: Optional[float] = Field(None, description="Bölünme/temettü düzeltmeli kapanış fiyatı")
    volume: Optional[float] = Field(None, description="İşlem hacmi")
    currency: str = Field("TRY", description="Fiyat para birimi")
    source_name: str = Field(..., description="Veri kaynağı (TradingView, yfinance vb.)")
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Verinin çekildiği an")


class MarketSeries(BaseModel):
    """
    Bir sembole ait tarihsel OHLCV serisi.
    Minimum teknik analiz için 200+ gün, tercihen 252+ gün gerekir.
    """
    symbol: str = Field(..., description="Kanonik sembol")
    timeframe: str = Field("1D", description="Zaman dilimi (1m, 5m, 1h, 1D vb.)")
    currency: str = Field("TRY", description="Para birimi")
    points: List[OHLCVPoint] = Field(default_factory=list, description="Kronolojik sıralı mum serisi")

    def count(self) -> int:
        return len(self.points)

    def is_sufficient_for_technicals(self) -> bool:
        """SMA200 ve 12M momentum için en az 200 mum var mı?"""
        return len(self.points) >= 200


class MarketQuote(BaseModel):
    """
    Anlık kotasyon / son fiyat snapshot'ı.
    """
    symbol: str = Field(..., description="Kanonik sembol")
    price: float = Field(..., description="Son işlem fiyatı")
    change: Optional[float] = Field(None, description="Günlük net değişim")
    change_percent: Optional[float] = Field(None, description="Günlük yüzde değişim")
    previous_close: Optional[float] = Field(None, description="Önceki gün kapanışı")
    open_price: Optional[float] = Field(None, description="Günün açılış fiyatı")
    day_high: Optional[float] = Field(None, description="Günün en yüksek fiyatı")
    day_low: Optional[float] = Field(None, description="Günün en düşük fiyatı")
    volume: Optional[float] = Field(None, description="Günlük toplam işlem hacmi")
    currency: str = Field("TRY", description="Para birimi")
    source_name: str = Field(..., description="Veri kaynağı")
    as_of_at: datetime = Field(default_factory=datetime.utcnow, description="Fiyatın ait olduğu an")
