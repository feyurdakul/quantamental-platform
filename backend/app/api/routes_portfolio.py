"""
Model Portföyü REST API Uç Noktaları (sistem_mimari.md Bölüm 10.4)
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.models.portfolio import PortfolioPosition, PortfolioSummary
from app.models.score import SignalType

portfolio_router = APIRouter(prefix="/v1/portfolio", tags=["Portfolio"])

# Bellek içi portföy deposu (Veritabanı ile senkronize)
PORTFOLIO_STORE: Dict[str, PortfolioPosition] = {
    "BIST:THYAO": PortfolioPosition(
        symbol="BIST:THYAO", name="Türk Hava Yolları",
        entry_price=280.0, current_price=330.0, quantity=100.0,
        sector="Transportation", signal=SignalType.BUY, composite_score=4.25
    ),
    "BIST:ASELS": PortfolioPosition(
        symbol="BIST:ASELS", name="Aselsan",
        entry_price=60.0, current_price=72.5, quantity=500.0,
        sector="Defense", signal=SignalType.STRONG_BUY, composite_score=4.60
    ),
    "NASDAQ:AAPL": PortfolioPosition(
        symbol="NASDAQ:AAPL", name="Apple Inc.",
        entry_price=220.0, current_price=311.38, quantity=20.0,
        sector="Technology", signal=SignalType.BUY, composite_score=4.10
    )
}


class AddPositionRequest(BaseModel):
    symbol: str
    name: str
    entry_price: float
    current_price: Optional[float] = None
    quantity: float = 1.0
    sector: Optional[str] = "Genel"


AddPositionRequest.model_rebuild()


def compute_portfolio_summary() -> PortfolioSummary:
    """Portföyün toplam değerini, ağırlıklarını ve sektör dağılımını hesaplar"""
    if not PORTFOLIO_STORE:
        return PortfolioSummary()

    total_val = sum(pos.current_value for pos in PORTFOLIO_STORE.values())
    total_cst = sum(pos.total_cost for pos in PORTFOLIO_STORE.values())
    total_pnl = total_val - total_cst
    pnl_pct = (total_pnl / total_cst * 100.0) if total_cst > 0 else 0.0

    # Her pozisyonun portföy ağırlığını ve verisini hesaplama
    positions_with_weights = []
    sector_values: Dict[str, float] = {}

    for pos in PORTFOLIO_STORE.values():
        weight = (pos.current_value / total_val) if total_val > 0 else 0.0
        sec = pos.sector or "Diğer"
        sector_values[sec] = sector_values.get(sec, 0.0) + pos.current_value

        positions_with_weights.append({
            "symbol": pos.symbol,
            "name": pos.name,
            "entry_date": pos.entry_date,
            "entry_price": pos.entry_price,
            "current_price": pos.current_price,
            "quantity": pos.quantity,
            "total_cost": pos.total_cost,
            "current_value": pos.current_value,
            "unrealized_pnl": pos.unrealized_pnl,
            "unrealized_pnl_percent": pos.unrealized_pnl_percent,
            "weight": round(weight, 4),
            "weight_percent": round(weight * 100.0, 2),
            "sector": pos.sector,
            "signal": pos.signal.value,
            "composite_score": pos.composite_score
        })

    # Sektör dağılımı yüzdeleri
    sector_allocations = {
        sec: round((val / total_val) * 100.0, 2)
        for sec, val in sector_values.items()
    } if total_val > 0 else {}

    return PortfolioSummary(
        total_value=round(total_val, 2),
        total_cost=round(total_cst, 2),
        total_pnl=round(total_pnl, 2),
        total_pnl_percent=round(pnl_pct, 2),
        position_count=len(PORTFOLIO_STORE),
        positions=positions_with_weights,
        sector_allocation=sector_allocations,
        updated_at=datetime.now(timezone.utc)
    )


@portfolio_router.get("")
async def get_portfolio() -> PortfolioSummary:
    """Model portföy özetini ve ağırlıklı pozisyonlarını getirir"""
    return compute_portfolio_summary()


@portfolio_router.post("/positions")
async def add_position(req: AddPositionRequest):
    """Portföye yeni pozisyon ekler veya mevcudu günceller"""
    cur_price = req.current_price if req.current_price is not None else req.entry_price
    pos = PortfolioPosition(
        symbol=req.symbol,
        name=req.name,
        entry_price=req.entry_price,
        current_price=cur_price,
        quantity=req.quantity,
        sector=req.sector
    )
    PORTFOLIO_STORE[req.symbol] = pos
    return {"message": "Pozisyon başarıyla eklendi", "position": pos}


@portfolio_router.delete("/positions/{symbol:path}")
async def delete_position(symbol: str):
    """Portföyden pozisyon siler"""
    if symbol in PORTFOLIO_STORE:
        del PORTFOLIO_STORE[symbol]
        return {"message": f"{symbol} portföyden kaldırıldı"}
    raise HTTPException(status_code=404, detail="Pozisyon bulunamadı")
