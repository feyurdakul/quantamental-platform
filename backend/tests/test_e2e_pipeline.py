"""
Uçtan Uca (E2E) Entegrasyon ve API Testleri
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.asset import Asset, AssetClass
from app.models.financials import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    MarketContext,
    FinancialSnapshot
)
from app.models.market_data import OHLCVPoint, MarketSeries
from app.scan.service import ScanOrchestrator
from datetime import date, datetime, timezone, timedelta

client = TestClient(app)


def test_health_endpoint():
    """Health check endpoint testi"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["providers_active"]) == 7


def test_e2e_scan_and_api_flow():
    """Tam tarama döngüsü ve API uç noktaları doğrulaması"""
    # 1. Evren listesini oku
    res_univ = client.get("/v1/universe")
    assert res_univ.status_code == 200
    assert res_univ.json()["count"] > 0

    # 2. Taramayı başlat
    res_scan = client.post("/v1/scan/start")
    assert res_scan.status_code == 200
    scan_data = res_scan.json()
    assert scan_data["total_assets"] > 0

    # 3. Dashboard durumunu sorgula
    res_dash = client.get("/v1/dashboard/summary")
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert "leaderboards" in dash_data
    assert dash_data["scan_stage"] in ["INIT", "FETCHING", "SCORING", "BENCHMARKS", "COMPLETED", "IDLE"]

    # 4. Tek bir varlığın 360° detayını sorgula
    res_asset = client.get("/v1/asset/BIST:THYAO")
    assert res_asset.status_code == 200
    asset_data = res_asset.json()
    assert asset_data["asset"]["symbol"] == "BIST:THYAO"
