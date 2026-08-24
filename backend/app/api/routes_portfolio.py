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

from app.db.repositories import PortfolioRepository, AssetRepository
from app.scan.service import ScanOrchestrator
from app.api.routes import orchestrator


class AddPositionRequest(BaseModel):
    symbol: str
    name: str
    entry_price: float
    current_price: Optional[float] = None
    quantity: float = 100.0
    target_weight_percent: float = 10.0
    sector: Optional[str] = "Genel"
    is_auto_managed: bool = False


class SellPositionRequest(BaseModel):
    symbol: str
    sell_percent: float = Field(100.0, ge=1.0, le=100.0, description="Satılacak yüzde (örn: 25, 50, 75, 100)")
    current_price: Optional[float] = None


AddPositionRequest.model_rebuild()
SellPositionRequest.model_rebuild()


def format_duration(entry_time_str: str) -> str:
    """Giriş zaman damgasından bu yana geçen süreyi hesaplar"""
    if not entry_time_str:
        return "Bugün"
    try:
        # ISO string parsing
        clean_str = entry_time_str.replace("Z", "+00:00")
        if "T" in clean_str:
            dt = datetime.fromisoformat(clean_str)
        else:
            dt = datetime.strptime(clean_str[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        delta = now - dt
        days = delta.days
        hours = delta.seconds // 3600
        mins = (delta.seconds % 3600) // 60

        if days > 30:
            return f"{days // 30} Ay {days % 30} Gün"
        elif days > 0:
            return f"{days} Gün {hours} Sa"
        elif hours > 0:
            return f"{hours} Saat {mins} Dk"
        elif mins > 0:
            return f"{mins} Dakika"
        else:
            return "Yeni Alım (< 1 Dk)"
    except Exception:
        return "Bugün"


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
        sc = orchestrator.status.results.get(sym)
        if not sc or not sc.get("technicals", {}).get("current_price"):
            # Canlı fiyat hafızada yoksa, hızlı piyasa verisi çek
            try:
                asset = AssetRepository.get_by_symbol(sym)
                if asset:
                    from app.scan.market_fetcher import LiveMarketFetcher
                    from app.scan.pipeline import AssetScanPipeline
                    m_series = LiveMarketFetcher.fetch_market_series_fast(asset)
                    fin_snaps = LiveMarketFetcher.fetch_financial_snapshots_fast(asset) if asset.requires_financials else []
                    res = AssetScanPipeline.process_asset(asset, m_series, fin_snaps)
                    if res.get("success"):
                        orchestrator.status.results[sym] = res
                        sc = res
            except Exception:
                pass

        sc = sc or {}
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
        pos_objs.append({
            "pos": pos,
            "raw": p
        })

    total_val = sum(item["pos"].current_value for item in pos_objs)
    total_cst = sum(item["pos"].total_cost for item in pos_objs)
    total_pnl = total_val - total_cst
    pnl_pct = (total_pnl / total_cst * 100.0) if total_cst > 0 else 0.0

    positions_with_weights = []
    sector_values: Dict[str, float] = {}

    for item in pos_objs:
        pos = item["pos"]
        raw = item["raw"]
        weight = (pos.current_value / total_val) if total_val > 0 else 0.0
        sec = pos.sector or "Diğer"
        sector_values[sec] = sector_values.get(sec, 0.0) + pos.current_value

        entry_ts = raw.get("entry_timestamp", "")
        duration_str = format_duration(entry_ts)

        positions_with_weights.append({
            "symbol": pos.symbol,
            "name": pos.name,
            "entry_date": str(entry_ts)[:16] if entry_ts else str(pos.entry_date),
            "holding_duration": duration_str,
            "entry_price": pos.entry_price,
            "current_price": pos.current_price,
            "quantity": pos.quantity,
            "total_cost": pos.total_cost,
            "current_value": pos.current_value,
            "unrealized_pnl": pos.unrealized_pnl,
            "unrealized_pnl_percent": pos.unrealized_pnl_percent,
            "target_weight_percent": raw.get("target_weight_percent", 10.0),
            "weight": round(weight, 4),
            "weight_percent": round(weight * 100.0, 2),
            "sector": pos.sector,
            "signal": pos.signal.value if hasattr(pos.signal, "value") else str(pos.signal),
            "composite_score": pos.composite_score,
            "is_auto_managed": raw.get("is_auto_managed", False)
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
        target_weight_percent=req.target_weight_percent,
        sector=req.sector,
        is_auto_managed=req.is_auto_managed
    )
    return {"message": f"{req.symbol} portföye kalıcı olarak eklendi (%{req.target_weight_percent} Ağırlık)"}


@portfolio_router.post("/positions/sell")
async def sell_position(req: SellPositionRequest):
    """Portföydeki bir pozisyondan kısmi veya tam satış yapar ve kârı realize eder"""
    # Canlı fiyatı bul
    cur_price = req.current_price
    if cur_price is None:
        sc = orchestrator.status.results.get(req.symbol, {})
        cur_price = sc.get("technicals", {}).get("current_price") or 100.0

    res = PortfolioRepository.partial_sell(req.symbol, req.sell_percent, cur_price)
    if res.get("success"):
        return res
    raise HTTPException(status_code=400, detail=res.get("message", "Satış işlemi başarısız"))


@portfolio_router.get("/trades")
async def get_trade_history():
    """Model portföy alım/satım işlem geçmişini getirir"""
    return PortfolioRepository.get_trades()


@portfolio_router.post("/auto-sync")
async def trigger_auto_sync():
    """
    Sinyallere göre otomatik portföy dengelemesini manuel olarak tetikler:
    - En riskli listedeki hisseleri satar
    - En güçlü potansiyel liderlerini (%10 Strong Buy / %7 Buy) ekler
    """
    leaderboards = orchestrator._generate_leaderboards()
    top_potential = leaderboards.get("top_potential", [])
    most_risky = leaderboards.get("most_risky", [])
    result = PortfolioRepository.sync_auto_signals(top_potential, most_risky)
    return {
        "message": "Otomatik portföy senkronizasyonu tamamlandı",
        "details": result
    }


@portfolio_router.delete("/positions/{symbol:path}")
async def delete_position(symbol: str):
    """Portföyden pozisyonu kalıcı olarak siler"""
    success = PortfolioRepository.delete_position(symbol)
    if success:
        return {"message": f"{symbol} portföyden kalıcı olarak silindi"}
    raise HTTPException(status_code=404, detail="Pozisyon veritabanında bulunamadı")


