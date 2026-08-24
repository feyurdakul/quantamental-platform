"""
Google Finance REST API Adaptörü (KilimcininKorOglu/Google-Finance-Api)
Şirket profili, CEO, sektör, hisse haberleri ve 15sn SSE canlı akışı.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import httpx
from app.providers.base import BaseProvider
from app.providers.symbol_router import SymbolRouter
from app.models.market_data import MarketQuote


class GoogleFinanceProvider(BaseProvider):
    """
    Google Finance REST API (Go servisi: port 8080/8190) adaptörü.
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url

    @property
    def provider_name(self) -> str:
        return "GoogleFinance"

    async def fetch_quote(self, symbol: str) -> Optional[MarketQuote]:
        """
        /v1/quote/{ticker} endpoint'inden anlık kotasyon çeker.
        """
        gf_symbol = SymbolRouter.to_google_finance(symbol)
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                r = await client.get(f"{self.base_url}/v1/quote/{gf_symbol}")
                if r.status_code != 200:
                    return None
                data = r.json()

                price = data.get("price")
                if price is None:
                    return None

                return MarketQuote(
                    symbol=symbol,
                    price=float(price),
                    change=data.get("change"),
                    change_percent=data.get("changePercent"),
                    previous_close=data.get("previousClose"),
                    open_price=data.get("open"),
                    day_high=data.get("dayHigh"),
                    day_low=data.get("dayLow"),
                    volume=data.get("volume"),
                    currency=data.get("currency", "TRY"),
                    source_name=self.provider_name,
                    as_of_at=datetime.now(timezone.utc)
                )
            except Exception:
                return None

    async def fetch_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        /v1/company/{ticker} endpoint'inden CEO, sektör, çalışan sayısı ve 52 haftalık aralık çeker.
        """
        gf_symbol = SymbolRouter.to_google_finance(symbol)

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                r = await client.get(f"{self.base_url}/v1/company/{gf_symbol}")
                if r.status_code == 200:
                    return r.json()
                return None
            except Exception:
                return None

    async def fetch_news(self, symbol: str) -> List[Dict[str, Any]]:
        """
        /v1/news/{ticker} endpoint'inden hisseye özel haberleri çeker.
        """
        gf_symbol = SymbolRouter.to_google_finance(symbol)

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                r = await client.get(f"{self.base_url}/v1/news/{gf_symbol}")
                if r.status_code == 200:
                    return r.json().get("news", [])
                return []
            except Exception:
                return []
