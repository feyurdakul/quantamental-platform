"""
Finnhub Veri Sağlayıcı Adaptörü (finnhub-python)
Wall Street analist hedef fiyatları, tavsiye trendleri ve EPS kâr sürprizleri.
"""

from datetime import datetime, timezone
from typing import Optional, List
from app.providers.base import BaseProvider
from app.providers.symbol_router import SymbolRouter
from app.models.analyst import (
    AnalystEstimates,
    PriceTarget,
    RecommendationTrend,
    EarningsSurprise
)


class FinnhubProvider(BaseProvider):
    """
    Finnhub API İstemcisi.
    """

    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import finnhub
            self._client = finnhub.Client(api_key=self.api_key)
        return self._client

    @property
    def provider_name(self) -> str:
        return "Finnhub"

    async def fetch_analyst_estimates(self, symbol: str) -> Optional[AnalystEstimates]:
        """
        Finnhub'dan hedef fiyat, tavsiye dağılımı ve EPS sürprizlerini çeker.
        """
        fh_symbol = SymbolRouter.to_finnhub(symbol)

        try:
            # 1. Price Target
            pt_raw = self.client.price_target(fh_symbol)
            price_target = None
            if pt_raw and isinstance(pt_raw, dict) and pt_raw.get("targetMedian"):
                price_target = PriceTarget(
                    target_high=pt_raw.get("targetHigh"),
                    target_low=pt_raw.get("targetLow"),
                    target_mean=pt_raw.get("targetMean"),
                    target_median=pt_raw.get("targetMedian"),
                    currency="USD",
                    last_updated=datetime.now(timezone.utc)
                )

            # 2. Recommendation Trends
            rec_raw = self.client.recommendation_trends(fh_symbol)
            recommendations: List[RecommendationTrend] = []
            if isinstance(rec_raw, list):
                for item in rec_raw[:6]: # Son 6 aylık trend
                    recommendations.append(RecommendationTrend(
                        period=item.get("period", ""),
                        strong_buy=item.get("strongBuy", 0),
                        buy=item.get("buy", 0),
                        hold=item.get("hold", 0),
                        sell=item.get("sell", 0),
                        strong_sell=item.get("strongSell", 0)
                    ))

            # 3. Earnings Surprises (Son 4 Çeyrek)
            surprises_raw = self.client.company_earnings(fh_symbol, limit=4)
            surprises: List[EarningsSurprise] = []
            if isinstance(surprises_raw, list):
                for item in surprises_raw:
                    surprises.append(EarningsSurprise(
                        period=item.get("period", ""),
                        actual=item.get("actual"),
                        estimate=item.get("estimate"),
                        surprise=item.get("surprise"),
                        surprise_percent=item.get("surprisePercent")
                    ))

            return AnalystEstimates(
                symbol=symbol,
                price_target=price_target,
                recommendations=recommendations,
                earnings_surprises=surprises,
                source_name=self.provider_name,
                fetched_at=datetime.now(timezone.utc)
            )

        except Exception:
            return None
