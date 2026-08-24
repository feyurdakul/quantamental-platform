"""
Kanonik Skor, Sinyal ve Güven Seviyesi Modelleri (sistem_mimari.md Bölüm 8)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"         # Kritik metriklerin büyük bölümü geçerli (coverage >= 0.75)
    MEDIUM = "MEDIUM"     # Anlamlı ama eksik veri var (0.40 <= coverage < 0.75)
    LOW = "LOW"           # Karar için yetersiz kapsama (coverage < 0.40)


class SignalType(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    WATCH = "WATCH"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class MetricScoreDetail(BaseModel):
    """
    Tek bir alt metriğin puanlama detayı (1-5 puan).
    """
    metric_key: str = Field(..., description="Metrik kimliği (örn: pe_ratio, roe, net_debt_to_equity)")
    display_name: str = Field(..., description="Okunabilir metrik adı")
    raw_value: Optional[float] = Field(None, description="Ham hesaplanan sayısal değer")
    formatted_value: Optional[str] = Field(None, description="Formatlanmış değer (örn: '%18.4', '4.12x')")
    score: Optional[float] = Field(None, description="1.0 - 5.0 arası normalize puan")
    weight: float = Field(1.0, description="Kategori içindeki ağırlığı")
    is_valid: bool = Field(True, description="Puan hesaplamaya katıldı mı?")
    status: str = Field("valid", description="valid, missing, invalid, insufficient_data, structural_na")
    notes: Optional[str] = Field(None, description="Açıklama veya teşhis bayrağı")


class CategoryScoreDetail(BaseModel):
    """
    Ana Kategori Puanı (Değerleme, Kalite, Dayanıklılık, Büyüme, Teknik Görünüm)
    """
    category_key: str = Field(..., description="Kategori kodu (valuation, quality, resilience, growth, technical)")
    category_name: str = Field(..., description="Kategori adı")
    category_score: Optional[float] = Field(None, description="1.0 - 5.0 kategori ağırlıklı puanı")
    theoretical_weight: float = Field(..., description="Şablondaki teorik kategori ağırlığı (örn: 0.25)")
    effective_weight: float = Field(..., description="Uygulanan etkin kategori ağırlığı")
    is_applicable: bool = Field(True, description="Bu varlık sınıfına uygulanabilir mi?")
    metrics: List[MetricScoreDetail] = Field(default_factory=list, description="Kategori altındaki metrikler")


class ScoreResult(BaseModel):
    """
    Bir varlığa ait nihai bileşik skor, sinyal ve güven seviyesi paketi (sistem_mimari.md Bölüm 8).
    """
    symbol: str = Field(..., description="Kanonik sembol")
    composite_score: float = Field(..., description="1.0 - 5.0 arası bileşik skor")
    confidence_level: ConfidenceLevel = Field(..., description="HIGH, MEDIUM, LOW")
    signal: SignalType = Field(..., description="STRONG_BUY, BUY, HOLD, WATCH, SELL, STRONG_SELL")
    coverage: float = Field(..., description="Kapsama oranı (kullanılan ağırlık / uygulanabilir ağırlık)")
    
    category_scores: Dict[str, CategoryScoreDetail] = Field(default_factory=dict, description="Kategori puanları")
    
    # Referans Dayanıklılık Modelleri (Ana skor ağırlığına açık sürüm olmadan katılmaz - Bölüm 7 & 8.4)
    altman_z_score: Optional[float] = Field(None, description="Altman Z-Score (5 bileşen)")
    piotroski_f_score: Optional[int] = Field(None, description="Piotroski F-Score (0-9 puan)")
    
    # Histerezis ve Sürümleme
    raw_score_before_hysteresis: Optional[float] = Field(None, description="Histerezis öncesi ham skor")
    hysteresis_applied: bool = Field(False, description="Skor bandı zıplamasını önleyen histerezis devrede mi?")
    formula_version: str = Field("1.0.0", description="Skor motoru formül sürümü")
    as_of_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Skorun üretildiği an")
    
    # Teşhis ve Uyarı Bayrakları
    flags: List[str] = Field(default_factory=list, description="Uyarı ve risk bayrakları (HIGH_TOTAL_LIABILITIES, comparability_limited vb.)")
