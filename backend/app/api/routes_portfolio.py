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

from app.db.repositories import PortfolioRepository
from app.scan.service import ScanOrchestrator
from app.api.routes import orchestrator


class AddPositionRequest(BaseModel):
    symbol: str
    name: str
    entry_price: float
    current_price: Optional[float] = None
    quantity: float = 100.0
    sector: Optional[str] = "Genel"


AddPositionRequest.model_rebuild()


def compute_portfolio_summary() -> PortfolioSummary:
    """Portföyün toplam değerini, ağırlıklarını ve sektör dağılımını veritabanından hesaplar"""
    db_positions = PortfolioRepository.get_all()
    if not db_positions:
        return PortfolioSummary(
            total_value=0.0,
            total_cost=0.0,
            total_pnl=0.0,
            total_pnl_percent=0.0,
            position_count=0,
            positions=[],
            sector_allocation={},
            updated_at=datetime.now(timezone.utc)
        )

    pos_objs = []
    for p in db_positions:
        sym = p["symbol"]
        # Canlı fiyat ve skor bilgisi
        sc = orchestrator.status.results.get(sym, {})
        sr = sc.get("score_result")
        cur_price = sc.get("technicals", {}).get("current_price") or p["entry_price"]
        sig = sr.signal if sr else SignalType.HOLD
        comp_score = sr.composite_score if sr else 6.0

        pos = PortfolioPosition(
            symbol=sym,
            name=p["name"],
            entry_price=p["entry_price"],
            current_price=cur_price,
            quantity=p["quantity"],
            sector=p.get("sector") or "Genel",
            signal=sig,
            composite_score=comp_score
        )
        pos_objs.append(pos)

    total_val = sum(pos.current_value for pos in pos_objs)
    total_cst = sum(pos.total_cost for pos in pos_objs)
    total_pnl = total_val - total_cst
    pnl_pct = (total_pnl / total_cst * 100.0) if total_cst > 0 else 0.0

    positions_with_weights = []
    sector_values: Dict[str, float] = {}

    for pos in pos_objs:
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
            "signal": pos.signal.value if hasattr(pos.signal, "value") else str(pos.signal),
            "composite_score": pos.composite_score
        })

    sector_allocations = {
        sec: round((val / total_val) * 100.0, 2)
        for sec, val in sector_values.items()
    } if total_val > 0 else {}

    return PortfolioSummary(
        total_value=round(total_val, 2),
        total_cost=round(total_cst, 2),
        total_pnl=round(total_pnl, 2),
        total_pnl_percent=round(pnl_pct, 2),
        position_count=len(pos_objs),
        positions=positions_with_weights,
        sector_allocation=sector_allocations,
        updated_at=datetime.now(timezone.utc)
    )


@portfolio_router.get("")
async def get_portfolio() -> PortfolioSummary:
    """Model portföy özetini ve ağırlıklı pozisyonlarını veritabanından kalıcı getirir"""
    return compute_portfolio_summary()


@portfolio_router.post("/positions")
async def add_position(req: AddPositionRequest):
    """Portföye yeni pozisyon ekler veya günceller (Veritabanına Kalıcı Yazar)"""
    PortfolioRepository.save_position(
        symbol=req.symbol,
        name=req.name,
        entry_price=req.entry_price,
        quantity=req.quantity,
        sector=req.sector
    )
    return {"message": f"{req.symbol} portföye kalıcı olarak eklendi"}


@portfolio_router.delete("/positions/{symbol:path}")
async def delete_position(symbol: str):
    """Portföyden pozisyonu kalıcı olarak siler"""
    success = PortfolioRepository.delete_position(symbol)
    if success:
        return {"message": f"{symbol} portföyden kalıcı olarak silindi"}
    raise HTTPException(status_code=404, detail="Pozisyon veritabanında bulunamadı")

