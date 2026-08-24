"""
Faz 1 Birim Testleri: Kanonik Modeller, Sembol Router ve Veri Doğrulama (sistem_mimari.md Bölüm 2, 3, 4)
"""

import pytest
from datetime import date, datetime
from app.models.asset import Asset, AssetClass, Exchange
from app.models.market_data import OHLCVPoint, MarketSeries, MarketQuote
from app.models.financials import (
    PeriodType,
    SnapshotStatus,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    MarketContext,
    FinancialSnapshot
)
from app.models.analyst import PriceTarget, RecommendationTrend, EarningsSurprise, AnalystEstimates
from app.models.score import (
    ConfidenceLevel,
    SignalType,
    MetricScoreDetail,
    CategoryScoreDetail,
    ScoreResult
)
from app.providers.symbol_router import SymbolRouter
from app.validation.quality_flags import QualityFlag, QualityChecker
from app.validation.financial_validator import FinancialValidator


def test_symbol_router_across_7_providers():
    """Tüm sağlayıcılar için sembol dönüşümünün doğrulanması"""
    bist_sym = "BIST:THYAO"
    us_sym = "NASDAQ:AAPL"
    crypto_sym = "BINANCE:BTCUSDT"
    fx_sym = "FX:USDTRY"

    # 1. isyatirimhisse
    assert SymbolRouter.to_isyatirim(bist_sym) == "THYAO"
    
    # 2. yfinance
    assert SymbolRouter.to_yfinance(bist_sym) == "THYAO.IS"
    assert SymbolRouter.to_yfinance(us_sym) == "AAPL"
    assert SymbolRouter.to_yfinance(crypto_sym, AssetClass.CRYPTO) == "BTC-USD"
    assert SymbolRouter.to_yfinance(fx_sym, AssetClass.FOREX) == "TRY=X"

    # 3. FMP
    assert SymbolRouter.to_fmp(bist_sym) == "THYAO.IS"
    assert SymbolRouter.to_fmp(us_sym) == "AAPL"
    assert SymbolRouter.to_fmp(crypto_sym) == "BTCUSD"

    # 4. Finnhub
    assert SymbolRouter.to_finnhub(us_sym) == "AAPL"
    assert SymbolRouter.to_finnhub(crypto_sym, AssetClass.CRYPTO) == "BINANCE:BTCUSDT"

    # 5. Google Finance
    assert SymbolRouter.to_google_finance(bist_sym) == "THYAO:IST"
    assert SymbolRouter.to_google_finance(us_sym) == "AAPL:NASDAQ"
    assert SymbolRouter.to_google_finance("NYSE:TSLA") == "TSLA:NYSE"
    assert SymbolRouter.to_google_finance(crypto_sym, AssetClass.CRYPTO) == "BTC-USD"
    assert SymbolRouter.to_google_finance(fx_sym, AssetClass.FOREX) == "USD-TRY"

    # 6. TradingView
    assert SymbolRouter.to_tradingview(bist_sym) == "BIST:THYAO"
    assert SymbolRouter.to_tradingview(us_sym) == "NASDAQ:AAPL"


def test_structural_na_rules():
    """ETF ve Kriptolar için şirket finansallarının structural_na olması kuralı (Bölüm 2 & 8.2)"""
    # Kripto için F/K oranı uygulanamaz
    assert not QualityChecker.is_structurally_applicable("pe_ratio", AssetClass.CRYPTO)
    # ETF için ROE uygulanamaz
    assert not QualityChecker.is_structurally_applicable("roe", AssetClass.ETF)
    # Hisse için F/K uygulanabilir
    assert QualityChecker.is_structurally_applicable("pe_ratio", AssetClass.BIST_STOCK)

    # Bankalar için Cari Oran ve Altman Z uygulanamaz (Bölüm 8.2)
    assert not QualityChecker.is_structurally_applicable("current_ratio", AssetClass.BANK_STOCK, is_bank_or_insurance=True)
    assert not QualityChecker.is_structurally_applicable("altman_z_score", AssetClass.BANK_STOCK, is_bank_or_insurance=True)
    # Bankalar için PD/DD ve ROE uygulanabilir
    assert QualityChecker.is_structurally_applicable("pb_ratio", AssetClass.BANK_STOCK, is_bank_or_insurance=True)
    assert QualityChecker.is_structurally_applicable("roe", AssetClass.BANK_STOCK, is_bank_or_insurance=True)


def test_financial_snapshot_validation_and_protection():
    """Geçerli snapshot kuralı ve eski geçerli verinin korunması (Bölüm 4.1 & İlke 4)"""
    # 1. Boş snapshot -> Geçersiz olmalı
    empty_snap = FinancialSnapshot(
        symbol="BIST:THYAO",
        period_end=date(2024, 6, 30),
        source_name="isyatirimhisse",
        currency="TRY"
    )
    assert not FinancialValidator.validate_snapshot(empty_snap)
    assert empty_snap.status == SnapshotStatus.INSUFFICIENT_DATA

    # 2. En az 2 anlamlı kalemi olan snapshot -> Geçerli olmalı
    valid_snap_2023 = FinancialSnapshot(
        symbol="BIST:THYAO",
        period_end=date(2023, 12, 31),
        source_name="isyatirimhisse",
        currency="TRY",
        income_statement=IncomeStatement(revenue=500_000_000_000, net_income=80_000_000_000),
        balance_sheet=BalanceSheet(total_assets=800_000_000_000, total_stockholders_equity=300_000_000_000)
    )
    assert FinancialValidator.validate_snapshot(valid_snap_2023)
    assert valid_snap_2023.status == SnapshotStatus.VALID

    # 3. Yeni gelen veri hatalı/boş ise -> Eski geçerli snapshot EZİLEMEZ (İlke 4)
    should_replace = FinancialValidator.should_replace_existing_snapshot(
        current_valid_snapshot=valid_snap_2023,
        incoming_snapshot=empty_snap
    )
    assert not should_replace

    # 4. Yeni gelen veri geçerli ve daha güncel ise -> Güncellenir
    valid_snap_2024 = FinancialSnapshot(
        symbol="BIST:THYAO",
        period_end=date(2024, 12, 31),
        source_name="isyatirimhisse",
        currency="TRY",
        income_statement=IncomeStatement(revenue=650_000_000_000, net_income=95_000_000_000),
        balance_sheet=BalanceSheet(total_assets=950_000_000_000, total_stockholders_equity=380_000_000_000)
    )
    assert FinancialValidator.should_replace_existing_snapshot(
        current_valid_snapshot=valid_snap_2023,
        incoming_snapshot=valid_snap_2024
    )
