"""
Analist Tahminleri, Hedef Fiyat ve Kâr Sürprizi Modelleri (Finnhub & Google Finance)
"""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field


class PriceTarget(BaseModel):
    """
    Wall Street Analist Hedef Fiyat Dağılımı (Finnhub)
    """
    target_high: Optional[float] = Field(None, description="En yüksek hedef fiyat")
    target_low: Optional[float] = Field(None, description="En düşük hedef fiyat")
    target_mean: Optional[float] = Field(None, description="Ortalama hedef fiyat")
    target_median: Optional[float] = Field(None, description="Medyan hedef fiyat")
    currency: str = Field("USD", description="Para birimi")
    last_updated: Optional[datetime] = Field(None, description="Son güncelleme zamanı")


class RecommendationTrend(BaseModel):
    """
    Analist Tavsiye Dağılımı (Finnhub)
    """
    period: str = Field(..., description="Dönem (örn: 2026-08-01)")
    strong_buy: int = Field(0, description="Güçlü Al tavsiyesi veren analist sayısı")
    buy: int = Field(0, description="Al tavsiyesi veren analist sayısı")
    hold: int = Field(0, description="Tut tavsiyesi veren analist sayısı")
    sell: int = Field(0, description="Sat tavsiyesi veren analist sayısı")
    strong_sell: int = Field(0, description="Güçlü Sat tavsiyesi veren analist sayısı")

    def total_analysts(self) -> int:
        return self.strong_buy + self.buy + self.hold + self.sell + self.strong_sell


class EarningsSurprise(BaseModel):
    """
    Çeyreklik EPS Kâr Sürprizi (Finnhub)
    """
    period: str = Field(..., description="Bilanço dönemi")
    actual: Optional[float] = Field(None, description="Açıklanan gerçekleşen EPS")
    estimate: Optional[float] = Field(None, description="Konsensüs beklenen EPS")
    surprise: Optional[float] = Field(None, description="Net sürpriz farkı")
    surprise_percent: Optional[float] = Field(None, description="Yüzde sürpriz (Beat/Miss %)")


class AnalystEstimates(BaseModel):
    """
    Bir sembole ait konsolide analist tahmin paketi.
    """
    symbol: str = Field(..., description="Kanonik sembol")
    price_target: Optional[PriceTarget] = Field(None, description="Hedef fiyatlar")
    recommendations: List[RecommendationTrend] = Field(default_factory=list, description="Aylık tavsiye trendleri")
    earnings_surprises: List[EarningsSurprise] = Field(default_factory=list, description="Son çeyrek kâr sürprizleri")
    source_name: str = Field("Finnhub", description="Veri sağlayıcı")
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Çekildiği an")
