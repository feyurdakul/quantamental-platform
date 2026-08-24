"""
Model Portföyü Veri Modelleri (sistem_mimari.md Bölüm 10.4)
Seçilmiş varlıklar, giriş anı maliyeti, güncel değer, ağırlık ve portföy risk/çeşitlendirme görünümü.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from app.models.score import SignalType


class PortfolioPosition(BaseModel):
    """
    Model portföyündeki tek bir varlık pozisyonu.
    """
    symbol: str = Field(..., description="Kanonik sembol (örn: BIST:THYAO)")
    name: str = Field(..., description="Varlık adı")
    entry_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Portföye giriş tarihi")
    entry_price: float = Field(..., description="Giriş / maliyet fiyatı")
    current_price: float = Field(..., description="Güncel piyasa fiyatı")
    quantity: float = Field(1.0, description="Pozisyon adedi")
    sector: Optional[str] = Field(None, description="Sektör")
    
    # Skorlama ve Sinyal Durumu
    signal: SignalType = Field(SignalType.HOLD, description="Mevcut sistem sinyali")
    composite_score: Optional[float] = Field(None, description="Mevcut bileşik skor")

    @property
    def total_cost(self) -> float:
        """Toplam Giriş Maliyeti"""
        return round(self.entry_price * self.quantity, 2)

    @property
    def current_value(self) -> float:
        """Toplam Güncel Değer"""
        return round(self.current_price * self.quantity, 2)

    @property
    def unrealized_pnl(self) -> float:
        """Realize Edilmemiş Net Kâr/Zarar"""
        return round(self.current_value - self.total_cost, 2)

    @property
    def unrealized_pnl_percent(self) -> float:
        """Realize Edilmemiş Yüzde Kâr/Zarar"""
        if self.total_cost == 0:
            return 0.0
        return round(((self.current_value - self.total_cost) / self.total_cost) * 100.0, 2)


class PortfolioSummary(BaseModel):
    """
    Konsolide Model Portföy Özeti.
    """
    total_value: float = Field(0.0, description="Portföy toplam güncel piyasa değeri")
    total_cost: float = Field(0.0, description="Portföy toplam alış maliyeti")
    total_pnl: float = Field(0.0, description="Portföy toplam net kâr/zarar")
    total_pnl_percent: float = Field(0.0, description="Portföy toplam yüzde getirisi")
    position_count: int = Field(0, description="Açık pozisyon sayısı")
    
    # Pozisyon Listesi (Her birinin portföy ağırlığı hesaplanmış)
    positions: List[Dict] = Field(default_factory=list, description="Ağırlıklı pozisyon listesi")
    
    # Sektör Bazlı Çeşitlendirme Dağılımı (% ağırlıklar)
    sector_allocation: Dict[str, float] = Field(default_factory=dict, description="Sektör çeşitlendirme ağırlıkları")
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Hesaplama anı")
