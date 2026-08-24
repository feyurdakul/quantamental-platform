"""
Faz 3 Birim Testleri: Hesaplama Motorları (sistem_mimari.md Bölüm 5, 6, 7, 8)
"""

import pytest
from datetime import date, datetime, timedelta, timezone
from app.models.asset import Asset, AssetClass
from app.models.market_data import OHLCVPoint
from app.models.financials import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    MarketContext,
    FinancialSnapshot
)
from app.engine.technical import TechnicalEngine
from app.engine.fundamental import FundamentalEngine
from app.engine.resilience import ResilienceEngine
from app.engine.scorer import ScorerEngine


def test_technical_engine():
    """Teknik motor hesaplamalarının doğrulanması (Bölüm 5)"""
    # 250 günlük yapay kapanış serisi (artan trend)
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    points = []
    price = 100.0
    for i in range(260):
        price += 0.5 if i % 2 == 0 else -0.2 # İstikrarlı yükseliş trendi
        points.append(OHLCVPoint(
            timestamp=base_date + timedelta(days=i),
            open=price - 0.2, high=price + 0.5, low=price - 0.5, close=price,
            adjusted_close=price, volume=100000.0, currency="TRY", source_name="TV"
        ))

    tech = TechnicalEngine.compute_all_technicals(points)
    
    assert tech["current_price"] > 100.0
    assert tech["sma50"] is not None
    assert tech["sma200"] is not None
    assert tech["rsi14"] is not None
    assert 0.0 <= tech["rsi14"] <= 100.0
    assert tech["return_1m"] is not None
    assert tech["return_12m"] is not None
    assert tech["annualized_volatility"] is not None
    assert tech["trend_regime"] == "POSITIVE"


def test_fundamental_engine_and_resilience():
    """Temel analiz oranları, Altman Z ve Piotroski F hesaplamaları (Bölüm 6 & 7)"""
    snap_2023 = FinancialSnapshot(
        symbol="BIST:THYAO", period_end=date(2023, 12, 31),
        source_name="isyatirimhisse", currency="TRY",
        income_statement=IncomeStatement(
            revenue=500_000_000_000, gross_profit=150_000_000_000,
            operating_income=100_000_000_000, ebitda=120_000_000_000,
            interest_expense=10_000_000_000, net_income=70_000_000_000,
            eps_diluted=20.0
        ),
        balance_sheet=BalanceSheet(
            cash_and_short_term_investments=80_000_000_000,
            total_current_assets=200_000_000_000, total_current_liabilities=120_000_000_000,
            total_assets=800_000_000_000, total_debt=100_000_000_000,
            total_liabilities=400_000_000_000, total_stockholders_equity=400_000_000_000,
            retained_earnings=250_000_000_000
        ),
        cash_flow=CashFlowStatement(
            operating_cash_flow=110_000_000_000, capital_expenditure=30_000_000_000,
            free_cash_flow=80_000_000_000
        ),
        market_context=MarketContext(
            current_price=300.0, market_cap=420_000_000_000, shares_outstanding=1_400_000_000
        )
    )

    snap_2024 = FinancialSnapshot(
        symbol="BIST:THYAO", period_end=date(2024, 12, 31),
        source_name="isyatirimhisse", currency="TRY",
        income_statement=IncomeStatement(
            revenue=650_000_000_000, gross_profit=200_000_000_000,
            operating_income=130_000_000_000, ebitda=155_000_000_000,
            interest_expense=12_000_000_000, net_income=90_000_000_000,
            eps_diluted=25.7
        ),
        balance_sheet=BalanceSheet(
            cash_and_short_term_investments=110_000_000_000,
            total_current_assets=260_000_000_000, total_current_liabilities=150_000_000_000,
            total_assets=1_000_000_000_000, total_debt=120_000_000_000,
            total_liabilities=500_000_000_000, total_stockholders_equity=500_000_000_000,
            retained_earnings=320_000_000_000
        ),
        cash_flow=CashFlowStatement(
            operating_cash_flow=140_000_000_000, capital_expenditure=40_000_000_000,
            free_cash_flow=100_000_000_000
        ),
        market_context=MarketContext(
            current_price=330.0, market_cap=462_000_000_000, shares_outstanding=1_400_000_000
        )
    )

    # 1. Değerleme
    val = FundamentalEngine.calculate_valuation_metrics(snap_2024)
    assert val["pe_ratio"] is not None and val["pe_ratio"] > 0 # ~5.13x
    assert val["pb_ratio"] is not None and val["pb_ratio"] > 0 # ~0.92x
    assert val["ev_ebitda"] is not None
    assert val["fcf_yield"] is not None and val["fcf_yield"] > 0

    # 2. Kalite
    qual = FundamentalEngine.calculate_quality_metrics(snap_2024, snap_2023)
    assert qual["roe"] is not None and qual["roe"] > 0.15 # ~%20 ROE
    assert qual["operating_margin"] is not None and qual["operating_margin"] == 0.20 # %20 Faaliyet Marjı

    # 3. Büyüme
    grw = FundamentalEngine.calculate_growth_metrics([snap_2023, snap_2024])
    assert grw["revenue_growth"] == 0.30 # %30 Gelir Büyümesi
    assert grw["net_income_growth"] is not None

    # 4. Likidite & Borçluluk
    liq = FundamentalEngine.calculate_liquidity_and_leverage_metrics(snap_2024)
    assert liq["current_ratio"] > 1.5 # ~1.73x
    assert liq["net_debt_to_equity"] is not None and liq["net_debt_to_equity"] < 0.10 # Net nakitte

    # 5. Altman Z-Score
    z = ResilienceEngine.calculate_altman_z_score(snap_2024)
    assert z is not None and z > 1.8 # Güvenli bölgede

    # 6. Piotroski F-Score (9 Kriter)
    f_score = ResilienceEngine.calculate_piotroski_f_score([snap_2023, snap_2024])
    assert f_score["score"] is not None
    assert f_score["score"] >= 7 # Güçlü finansal durum (7-9 arası)


def test_scorer_engine_composite_and_signals():
    """Skor motorunun bileşik skor, sinyal ve güven seviyesi üretimi (Bölüm 8)"""
    asset = Asset(
        symbol="BIST:THYAO", name="Türk Hava Yolları",
        asset_class=AssetClass.BIST_STOCK, exchange="BIST", sector="Transportation"
    )

    technicals = {"rsi14": 52.0, "trend_regime": "POSITIVE", "price_vs_sma200": 0.12}
    valuation = {"pe_ratio": 5.13, "pb_ratio": 0.92}
    quality = {"roe": 0.20, "operating_margin": 0.20}
    growth = {"revenue_growth": 0.30, "base_effect_warning": False}
    liquidity = {"net_debt_to_equity": 0.05, "current_ratio": 1.73, "gross_debt_to_equity": 0.24, "flags": []}
    resilience = {"altman_z_score": 2.65, "piotroski_f_score": {"score": 8}}

    score_res = ScorerEngine.score_asset(
        asset=asset, technicals=technicals, valuation=valuation,
        quality=quality, growth=growth, liquidity=liquidity, resilience=resilience
    )

    assert score_res.composite_score >= 8.0
    assert score_res.confidence_level.value == "HIGH"
    assert score_res.signal.value in ["STRONG_BUY", "BUY"]
    assert score_res.coverage >= 0.75
    assert len(score_res.category_scores) == 5
    assert score_res.fundamental_rating is not None
    assert score_res.fundamental_rating["rating"] in ["S", "A"]
    assert score_res.fundamental_rating["total_score"] >= 19


def test_fundamental_rating_engine_explicit():
    """Kullanıcının 6-Faktörlü Temel Derecelendirme Motoru mantığı testi"""
    from app.engine.rating_model import FundamentalRatingEngine
    
    # 1. En iyi senaryo (Strong Buy / S notu)
    val_best = {"pe_ratio": 12.0, "pb_ratio": 1.2, "fcf_yield": 0.30}
    qual_best = {"roe": 0.25, "roa": 0.12, "fcf_margin": 0.30}
    liq_best = {"net_debt_to_equity": 0.15}
    
    r_best = FundamentalRatingEngine.compute_rating(val_best, qual_best, liq_best, is_financial_asset=True)
    assert r_best.total_score == 30
    assert r_best.rating == "S"
    assert r_best.recommendation == "Strong Buy"
    
    # 2. Zarar eden şirket (F/K negatif özel kuralı)
    val_loss = {"pe_ratio": -8.5, "pb_ratio": 12.0, "fcf_yield": -0.20}
    qual_loss = {"roe": -0.05, "roa": -0.02, "fcf_margin": -0.20}
    liq_loss = {"net_debt_to_equity": 3.5}
    
    r_loss = FundamentalRatingEngine.compute_rating(val_loss, qual_loss, liq_loss, is_financial_asset=True)
    assert r_loss.total_score == 6
    assert r_loss.rating == "D"
    assert r_loss.recommendation == "Strong Sell"
    assert r_loss.metric_breakdown["pe_ratio"]["points"] == 1

