"""
Yahoo Finance Veri Sağlayıcı Adaptörü (yfinance)
BIST ve ABD hisseleri için bölünme/temettü düzeltmeli OHLCV, tedavüldeki hisse sayısı ve yedek finansallar.
"""

from datetime import datetime, timezone
from typing import Optional, List
from app.providers.base import BaseProvider
from app.providers.symbol_router import SymbolRouter
from app.models.market_data import MarketSeries, OHLCVPoint, MarketQuote


class YFinanceProvider(BaseProvider):
    """
    yfinance kütüphanesi sarmalayıcısı.
    """

    @property
    def provider_name(self) -> str:
        return "yfinance"

    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1D", lookback_days: int = 300) -> Optional[MarketSeries]:
        """
        yfinance üzerinden Adjusted Close dahil tam OHLCV serisi çeker.
        """
        yf_symbol = SymbolRouter.to_yfinance(symbol)
        try:
            import yfinance as yf
            ticker = yf.Ticker(yf_symbol)
            # ~252 işlem günü için 1.5 yıllık periyot çekilir
            period_str = "2y" if lookback_days >= 200 else "1y"
            df = ticker.history(period=period_str)
            
            if df is None or df.empty:
                return None

            points: List[OHLCVPoint] = []
            for idx, row in df.iterrows():
                # Timestamp parsing
                ts = idx.to_pydatetime()
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)

                points.append(OHLCVPoint(
                    timestamp=ts,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    adjusted_close=float(row.get("Adj Close", row["Close"])),
                    volume=float(row["Volume"]) if "Volume" in row else None,
                    currency="TRY" if ".IS" in yf_symbol else "USD",
                    source_name=self.provider_name,
                    fetched_at=datetime.now(timezone.utc)
                ))

            return MarketSeries(
                symbol=symbol,
                timeframe=timeframe,
                currency="TRY" if ".IS" in yf_symbol else "USD",
                points=points
            )

        except Exception:
            return None

    async def fetch_quote(self, symbol: str) -> Optional[MarketQuote]:
        """
        yfinance anlık fiyat ve önceki kapanış bilgisi.
        """
        yf_symbol = SymbolRouter.to_yfinance(symbol)
        try:
            import yfinance as yf
            ticker = yf.Ticker(yf_symbol)
            fast_info = ticker.fast_info
            price = fast_info.last_price
            prev_close = fast_info.previous_close

            if price is None:
                return None

            change = (price - prev_close) if prev_close else None
            ch_pct = (change / prev_close * 100.0) if (change and prev_close) else None

            return MarketQuote(
                symbol=symbol,
                price=float(price),
                change=float(change) if change else None,
                change_percent=float(ch_pct) if ch_pct else None,
                previous_close=float(prev_close) if prev_close else None,
                currency="TRY" if ".IS" in yf_symbol else "USD",
                source_name=self.provider_name,
                as_of_at=datetime.now(timezone.utc)
            )
        except Exception:
            return None

    def fetch_shares_outstanding(self, symbol: str) -> Optional[float]:
        """Tedavüldeki hisse adedini çeker (Piotroski F için)"""
        yf_symbol = SymbolRouter.to_yfinance(symbol)
        try:
            import yfinance as yf
            ticker = yf.Ticker(yf_symbol)
            return ticker.info.get("sharesOutstanding") or ticker.fast_info.shares
        except Exception:
            return None
