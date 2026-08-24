"""
Model Portföyü Birim ve API Testleri (sistem_mimari.md Bölüm 10.4)
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.portfolio import PortfolioPosition
from app.models.score import SignalType

client = TestClient(app)


def test_portfolio_position_calculations():
    """Pozisyon maliyet, değer ve getiri hesaplama doğrulaması"""
    pos = PortfolioPosition(
        symbol="BIST:THYAO",
        name="Türk Hava Yolları",
        entry_price=250.0,
        current_price=300.0,
        quantity=10.0,
        sector="Transportation",
        signal=SignalType.BUY
    )

    assert pos.total_cost == 2500.0
    assert pos.current_value == 3000.0
    assert pos.unrealized_pnl == 500.0
    assert pos.unrealized_pnl_percent == 20.0


def test_portfolio_api_endpoints():
    """Portföy listeleme, ekleme ve silme API testleri"""
    # 1. Portföy özetini al
    res = client.get("/v1/portfolio")
    assert res.status_code == 200
    data = res.json()
    assert data["total_value"] > 0
    assert data["position_count"] >= 1
    assert "sector_allocation" in data

    # Ağırlıkların toplamının yaklaşık %100 olması
    weights_sum = sum(p["weight"] for p in data["positions"])
    assert round(weights_sum, 2) == 1.00

    # 2. Yeni pozisyon ekle
    add_payload = {
        "symbol": "NASDAQ:NVDA",
        "name": "NVIDIA Corp.",
        "entry_price": 120.0,
        "current_price": 135.0,
        "quantity": 15.0,
        "sector": "Technology"
    }
    res_add = client.post("/v1/portfolio/positions", json=add_payload)
    assert res_add.status_code == 200
    assert res_add.json()["position"]["symbol"] == "NASDAQ:NVDA"

    # 3. Eklenen pozisyonu sil
    res_del = client.delete("/v1/portfolio/positions/NASDAQ:NVDA")
    assert res_del.status_code == 200
