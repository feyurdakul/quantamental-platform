"""
Kanonik Finansal Tablolar ve Bilanço Snapshot Modelleri (sistem_mimari.md Bölüm 3.3 & 3.4)
"""

from datetime import datetime, date, timezone
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class PeriodType(str, Enum):
    ANNUAL = "annual"         # Yıllık Bilanço
    QUARTERLY = "quarterly"   # Çeyreklik Bilanço
    TTM = "ttm"               # Son On İki Ay (Trailing Twelve Months)
    MRQ = "mrq"               # En Son Çeyrek (Most Recent Quarter)


class SnapshotStatus(str, Enum):
    VALID = "valid"                             # Geçerli, kullanıma hazır snapshot
    MISSING = "missing"                         # Kaynak alanı yok
    INVALID = "invalid"                         # Matematiksel olarak anlamsız/bozuk
    INSUFFICIENT_DATA = "insufficient_data"     # Trend/model için yeterli dönem yok
    STRUCTURAL_NA = "structural_na"             # İlgili varlık sınıfına uygulanamaz (ETF, Kripto vb.)


class IncomeStatement(BaseModel):
    """
    Kanonik Gelir Tablosu Kalemleri (sistem_mimari.md Bölüm 3.3)
    """
    revenue: Optional[float] = Field(None, description="Toplam Hasılat / Gelir")
    cost_of_revenue: Optional[float] = Field(None, description="Satışların Maliyeti (COGS)")
    gross_profit: Optional[float] = Field(None, description="Brüt Kâr")
    operating_income: Optional[float] = Field(None, description="Faaliyet Kârı / EBIT")
    ebitda: Optional[float] = Field(None, description="FAVÖK")
    interest_expense: Optional[float] = Field(None, description="Faiz Gideri")
    pretax_income: Optional[float] = Field(None, description="Vergi Öncesi Kâr")
    income_tax_expense: Optional[float] = Field(None, description="Dönem Vergi Gideri")
    net_income: Optional[float] = Field(None, description="Net Dönem Kârı")
    eps_diluted: Optional[float] = Field(None, description="Seyreltilmiş Hisse Başına Kâr")
    weighted_average_shares_diluted: Optional[float] = Field(None, description="Ağırlıklı Ortalama Hisse Sayısı")


class BalanceSheet(BaseModel):
    """
    Kanonik Bilanço Kalemleri (sistem_mimari.md Bölüm 3.3)
    """
    cash_and_short_term_investments: Optional[float] = Field(None, description="Nakit ve Benzerleri")
    accounts_receivable: Optional[float] = Field(None, description="Ticari Alacaklar")
    inventory: Optional[float] = Field(None, description="Stoklar")
    total_current_assets: Optional[float] = Field(None, description="Toplam Dönen Varlıklar")
    total_assets: Optional[float] = Field(None, description="Toplam Aktifler / Varlıklar")
    short_term_debt: Optional[float] = Field(None, description="Kısa Vadeli Finansal Borç")
    long_term_debt: Optional[float] = Field(None, description="Uzun Vadeli Finansal Borç")
    total_debt: Optional[float] = Field(None, description="Toplam Finansal Borç")
    accounts_payable: Optional[float] = Field(None, description="Ticari Borçlar")
    total_current_liabilities: Optional[float] = Field(None, description="Toplam Kısa Vadeli Yükümlülükler")
    total_liabilities: Optional[float] = Field(None, description="Toplam Yükümlülükler / Borçlar")
    total_stockholders_equity: Optional[float] = Field(None, description="Toplam Özsermaye")
    retained_earnings: Optional[float] = Field(None, description="Geçmiş Yıllar Kârları")


class CashFlowStatement(BaseModel):
    """
    Kanonik Nakit Akış Tablosu Kalemleri (sistem_mimari.md Bölüm 3.3)
    """
    operating_cash_flow: Optional[float] = Field(None, description="İşletme Faaliyetlerinden Nakit Akışı (OCF)")
    capital_expenditure: Optional[float] = Field(None, description="Yatırım Harcamaları (Capex)")
    free_cash_flow: Optional[float] = Field(None, description="Serbest Nakit Akışı (FCF = OCF - Capex)")
    depreciation_and_amortization: Optional[float] = Field(None, description="Amortisman ve İtfa Payları")
    share_issuance_or_repurchase: Optional[float] = Field(None, description="Hisse İhracı / Geri Alım Net Nakit")
    dividends_paid: Optional[float] = Field(None, description="Ödenen Temettüler")


class MarketContext(BaseModel):
    """
    Piyasa Değeri ve Bağlam Kalemleri (sistem_mimari.md Bölüm 3.3)
    """
    market_cap: Optional[float] = Field(None, description="Piyasa Değeri")
    enterprise_value: Optional[float] = Field(None, description="Firma Değeri (EV)")
    shares_outstanding: Optional[float] = Field(None, description="Tedavüldeki Hisse Adedi")
    current_price: Optional[float] = Field(None, description="Hesap anındaki hisse fiyatı")


class FinancialSnapshot(BaseModel):
    """
    Tek bir finansal döneme ait kanonik paket (sistem_mimari.md Bölüm 3.4 & 4.1).
    Her snapshot kaynak, dönem, sürüm ve durum metadata'sını eksiksiz taşır.
    """
    symbol: str = Field(..., description="Kanonik sembol")
    period_type: PeriodType = Field(PeriodType.ANNUAL, description="Dönem türü (annual/quarterly/ttm/mrq)")
    period_end: date = Field(..., description="Finansal dönemin bitiş tarihi")
    as_of_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Piyasa fiyatı ve hesap anı")
    source_name: str = Field(..., description="Veri kaynağı (isyatirimhisse, FMP, yfinance)")
    source_endpoint: Optional[str] = Field(None, description="Kaynak endpoint veya metod adı")
    currency: str = Field("TRY", description="Tablo para birimi")
    formula_version: str = Field("1.0.0", description="Hesaplama sürümü")
    status: SnapshotStatus = Field(SnapshotStatus.VALID, description="Veri geçerlilik durumu")
    is_usd_converted: bool = Field(False, description="TMS-29 enflasyon arındırması için USD'ye çevrilmiş mi?")
    comparability_limited: bool = Field(False, description="TMS-29 enflasyon muhasebesi karşılaştırma kısıtı bayrağı")

    income_statement: IncomeStatement = Field(default_factory=IncomeStatement)
    balance_sheet: BalanceSheet = Field(default_factory=BalanceSheet)
    cash_flow: CashFlowStatement = Field(default_factory=CashFlowStatement)
    market_context: MarketContext = Field(default_factory=MarketContext)

    def is_valid_financial_snapshot(self) -> bool:
        """
        sistem_mimari.md Bölüm 4.1 Geçerli Finansal Snapshot Kuralı:
        - Kaynak, para birimi ve period_end mevcut olmalı
        - En az iki anlamlı ana finansal kalem bulunmalı
        """
        if self.status != SnapshotStatus.VALID:
            return False
        
        valid_items_count = 0
        inc = self.income_statement
        bs = self.balance_sheet
        cf = self.cash_flow

        for val in [
            inc.revenue, inc.net_income, inc.operating_income,
            bs.total_assets, bs.total_stockholders_equity, bs.total_debt,
            cf.operating_cash_flow, cf.free_cash_flow
        ]:
            if val is not None and val != 0:
                valid_items_count += 1

        return valid_items_count >= 2
