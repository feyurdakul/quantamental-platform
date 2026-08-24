"""
TradingView Gateway Adaptörü (@mathieuc/tradingview Node.js köprüsü)
Milisaniyelik canlı mumlar, Pine Script indikatörleri ve TradingView TA konsensüsü.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import httpx
from app.providers.base import BaseProvider
from app.providers.symbol_router import SymbolRouter
from app.models.market_data import MarketSeries, OHLCVPoint


class TradingViewProvider(BaseProvider):
    """
    TradingView Node.js mikro servis adaptörü (port 3001).
    """

    def __init__(self, gateway_url: str = "http://localhost:3001"):
        self.gateway_url = gateway_url

    @property
    def provider_name(self) -> str:
        return "TradingView"

    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1D", lookback_days: int = 300) -> Optional[MarketSeries]:
        """
        TradingView Gateway'den canlı OHLCV barlarını çeker.
        """
        tv_symbol = SymbolRouter.to_tradingview(symbol)

        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                r = await client.get(f"{self.gateway_url}/ohlcv/{tv_symbol}?tf={timeframe}&bars={lookback_days}")
                if r.status_code != 200:
                    return None
                data = r.json()

                raw_bars = data.get("bars", [])
                if not raw_bars:
                    return None

                points: List[OHLCVPoint] = []
                for b in raw_bars:
                    ts = datetime.fromtimestamp(b.get("time"), tz=timezone.utc)
                    points.append(OHLCVPoint(
                        timestamp=ts,
                        open=float(b.get("open")),
                        high=float(b.get("max") or b.get("high")),
                        low=float(b.get("min") or b.get("low")),
                        close=float(b.get("close")),
                        volume=float(b.get("volume")) if b.get("volume") is not None else None,
                        currency="TRY" if "BIST" in tv_symbol else "USD",
                        source_name=self.provider_name,
                        fetched_at=datetime.now(timezone.utc)
                    ))

                return MarketSeries(
                    symbol=symbol,
                    timeframe=timeframe,
                    currency="TRY" if "BIST" in tv_symbol else "USD",
                    points=points
                )
            except Exception:
                return None

    async def fetch_ta_consensus(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        TradingView yerleşik teknik analiz konsensüsünü (Strong Buy/Sell) çeker.
        """
        tv_symbol = SymbolRouter.to_tradingview(symbol)

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                r = await client.get(f"{self.gateway_url}/ta/{tv_symbol}")
                if r.status_code == 200:
                    return r.json()
                return None
            except Exception:
                return None
