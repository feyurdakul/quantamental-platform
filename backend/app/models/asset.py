"""
Varlık Kimliği ve Evren Modelleri (sistem_mimari.md Bölüm 2 & 3.1)
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    BIST_STOCK = "BIST_STOCK"         # BIST Sanayi / Ticaret Hissesi
    US_STOCK = "US_STOCK"             # ABD Hisse Senedi (NASDAQ, NYSE)
    BANK_STOCK = "BANK_STOCK"         # Banka / Sigorta / Finansal Kurum (Özel Şablon)
    ETF = "ETF"                       # Borsa Yatırım Fonu (ETF)
    CRYPTO = "CRYPTO"                 # Kripto Para (Spot/Futures)
    FOREX = "FOREX"                   # Döviz Çifti
    COMMODITY = "COMMODITY"           # Emtia (Altın, Petrol vb.)
    INDEX = "INDEX"                   # Borsa Endeksi (XU100, SPX vb.)


class Exchange(str, Enum):
    BIST = "BIST"                     # Borsa İstanbul (IST)
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
    AMEX = "AMEX"
    BINANCE = "BINANCE"
    COINBASE = "COINBASE"
    FX = "FX"
    TVC = "TVC"                       # TradingView Commodities / Indices
    FRED = "FRED"                     # Federal Reserve Macro


class Asset(BaseModel):
    """
    Kanonik Varlık Kimliği Modeli.
    Uygulama genelinde sembol formatı: 'BORSA:SEMBOL' (örn: 'BIST:THYAO', 'NASDAQ:AAPL')
    """
    symbol: str = Field(..., description="Kanonik sembol (örn: BIST:THYAO, NASDAQ:AAPL)")
    name: str = Field(..., description="Varlık tam adı")
    asset_class: AssetClass = Field(..., description="Varlık sınıfı")
    exchange: str = Field(..., description="İşlem gördüğü borsa")
    sector: Optional[str] = Field(None, description="Sektör (Hisseler için zorunlu)")
    industry: Optional[str] = Field(None, description="Alt sektör / endüstri")
    currency: str = Field("TRY", description="Fiyat ve finansal tablo para birimi")
    is_active: bool = Field(True, description="Aktif tarama evreninde mi?")
    requires_financials: bool = Field(True, description="Temel bilanço analizi gerektirir mi?")

    def is_financial_institution(self) -> bool:
        """Banka veya sigorta gibi özel bilanço şablonu gerektiren kurum mu?"""
        return self.asset_class == AssetClass.BANK_STOCK or (
            self.sector is not None and any(k in self.sector.lower() for k in ["bank", "insurance", "financial", "sigorta"])
        )
