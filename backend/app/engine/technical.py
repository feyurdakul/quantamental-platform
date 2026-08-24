"""
Teknik Hesaplama Motoru (sistem_mimari.md Bölüm 5)
Günlük OHLCV serisinden SMA50, SMA200, RSI(14), Momentum (1M/3M/6M/12M) ve Volatilite hesaplar.
"""

import math
from typing import List, Dict, Optional, Any
from app.models.market_data import OHLCVPoint


class TechnicalEngine:
    """
    Kanonik OHLCV serisi üzerinde teknik analiz metriklerini hesaplar.
    Minimum veri gereksinimi: 200 gün (tercihen 252+ gün).
    """

    @staticmethod
    def calculate_sma(closes: List[float], period: int) -> Optional[float]:
        """Basit Hareketli Ortalama (SMA)"""
        if len(closes) < period:
            return None
        return sum(closes[-period:]) / period

    @staticmethod
    def calculate_rsi(closes: List[float], period: int = 14) -> Optional[float]:
        """
        14 dönemlik Wilder's Relative Strength Index (RSI).
        (sistem_mimari.md Bölüm 5.2)
        """
        if len(closes) < period + 1:
            return None

        # Fiyat farkları
        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [max(d, 0.0) for d in deltas]
        losses = [abs(min(d, 0.0)) for d in deltas]

        # İlk periyot için basit ortalama
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        # Wilder's Düzeltmesi (Exponential Smoothing)
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0.0:
            return 100.0 if avg_gain > 0.0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return round(rsi, 2)

    @staticmethod
    def calculate_return(closes: List[float], lookback_days: int) -> Optional[float]:
        """
        Tarihsel Getiri / Momentum: (close_t / close_(t-n)) - 1
        (sistem_mimari.md Bölüm 5.3)
        """
        if len(closes) <= lookback_days:
            return None
        current_price = closes[-1]
        past_price = closes[-(lookback_days + 1)]
        if past_price <= 0:
            return None
        return (current_price / past_price) - 1.0

    @staticmethod
    def calculate_annualized_volatility(closes: List[float], lookback_days: int = 252) -> Optional[float]:
        """
        Yıllıklandırılmış Volatilite: std(daily_return) × √252
        (sistem_mimari.md Bölüm 5.4)
        """
        available_days = min(len(closes) - 1, lookback_days)
        if available_days < 20:
            return None

        recent_closes = closes[-(available_days + 1):]
        daily_returns = [
            (recent_closes[i] / recent_closes[i - 1]) - 1.0
            for i in range(1, len(recent_closes))
            if recent_closes[i - 1] > 0
        ]

        n = len(daily_returns)
        if n < 20:
            return None

        mean = sum(daily_returns) / n
        variance = sum((r - mean) ** 2 for r in daily_returns) / (n - 1)
        std_dev = math.sqrt(variance)
        annualized_vol = std_dev * math.sqrt(252)
        return round(annualized_vol, 4)

    @classmethod
    def compute_all_technicals(cls, points: List[OHLCVPoint]) -> Dict[str, Any]:
        """
        Verilen OHLCV serisi için tüm teknik metrikleri hesaplar.
        """
        if not points:
            return {}

        # Zaman damgasına göre sıralı kapanış fiyatları (tercihen adjusted_close)
        sorted_points = sorted(points, key=lambda p: p.timestamp)
        closes = [
            p.adjusted_close if p.adjusted_close is not None else p.close
            for p in sorted_points
        ]
        
        current_price = closes[-1]
        sma50 = cls.calculate_sma(closes, 50)
        sma200 = cls.calculate_sma(closes, 200)
        rsi14 = cls.calculate_rsi(closes, 14)
        
        # Momentum dönemleri (İşlem günü bazlı yaklaşık periyotlar)
        ret_1m = cls.calculate_return(closes, 21)   # 1 Ay (~21 işlem günü)
        ret_3m = cls.calculate_return(closes, 63)   # 3 Ay (~63 işlem günü)
        ret_6m = cls.calculate_return(closes, 126)  # 6 Ay (~126 işlem günü)
        ret_12m = cls.calculate_return(closes, 252) # 12 Ay (~252 işlem günü)

        volatility = cls.calculate_annualized_volatility(closes, 252)

        # Fiyat / SMA oranları ve Trend Rejimi
        price_vs_sma50 = (current_price / sma50 - 1.0) if (sma50 and sma50 > 0) else None
        price_vs_sma200 = (current_price / sma200 - 1.0) if (sma200 and sma200 > 0) else None
        trend_regime = "POSITIVE" if (sma50 and sma200 and sma50 > sma200) else "NEGATIVE" if (sma50 and sma200) else "NEUTRAL"

        return {
            "current_price": current_price,
            "sma50": round(sma50, 4) if sma50 else None,
            "sma200": round(sma200, 4) if sma200 else None,
            "price_vs_sma50": round(price_vs_sma50, 4) if price_vs_sma50 is not None else None,
            "price_vs_sma200": round(price_vs_sma200, 4) if price_vs_sma200 is not None else None,
            "trend_regime": trend_regime,
            "rsi14": rsi14,
            "return_1m": round(ret_1m, 4) if ret_1m is not None else None,
            "return_3m": round(ret_3m, 4) if ret_3m is not None else None,
            "return_6m": round(ret_6m, 4) if ret_6m is not None else None,
            "return_12m": round(ret_12m, 4) if ret_12m is not None else None,
            "annualized_volatility": volatility,
            "bar_count": len(closes)
        }
