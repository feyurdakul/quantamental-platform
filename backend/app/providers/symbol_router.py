"""
Evrensel Sembol Çevirici ve Yönlendirici (sistem_mimari.md Bölüm 3.1)
Kanonik 'BORSA:SEMBOL' formatını 7 sağlayıcının istediği özel formatlara dönüştürür.
"""

from typing import Optional, Dict
from app.models.asset import AssetClass


class SymbolRouter:
    """
    Kanonik sembolleri (örn: 'BIST:THYAO', 'NASDAQ:AAPL', 'BINANCE:BTCUSDT')
    sağlayıcıların özel sembol formatlarına çevirir.
    """

    @staticmethod
    def parse_canonical(canonical_symbol: str) -> tuple[str, str]:
        """
        'BORSA:SEMBOL' stringini (exchange, ticker) olarak ayrıştırır.
        Örnek: 'BIST:THYAO' -> ('BIST', 'THYAO')
        """
        parts = canonical_symbol.split(":")
        if len(parts) == 2:
            return parts[0].upper(), parts[1].upper()
        return "", canonical_symbol.upper()

    @classmethod
    def to_isyatirim(cls, canonical_symbol: str) -> str:
        """
        isyatirimhisse için sembol üretir (Sadece saf BIST ticker'ı).
        Örnek: 'BIST:THYAO' -> 'THYAO', 'BIST:GARAN' -> 'GARAN'
        """
        exchange, ticker = cls.parse_canonical(canonical_symbol)
        return ticker

    @classmethod
    def to_yfinance(cls, canonical_symbol: str, asset_class: Optional[AssetClass] = None) -> str:
        """
        yfinance için sembol üretir.
        Örnekler:
        - 'BIST:THYAO' -> 'THYAO.IS'
        - 'NASDAQ:AAPL' -> 'AAPL'
        - 'NYSE:TSLA' -> 'TSLA'
        - 'BINANCE:BTCUSDT' -> 'BTC-USD'
        - 'FX:USDTRY' -> 'TRY=X'
        - 'BIST:XU100' -> 'XU100.IS'
        """
        exchange, ticker = cls.parse_canonical(canonical_symbol)
        
        if exchange == "BIST":
            return f"{ticker}.IS"
        elif exchange in ["NASDAQ", "NYSE", "AMEX"]:
            return ticker
        elif exchange == "BINANCE" or asset_class == AssetClass.CRYPTO:
            # BTCUSDT -> BTC-USD
            if ticker.endswith("USDT"):
                base = ticker[:-4]
                return f"{base}-USD"
            return ticker
        elif exchange == "FX" or asset_class == AssetClass.FOREX:
            # USDTRY -> TRY=X, EURUSD -> EURUSD=X
            if ticker == "USDTRY":
                return "TRY=X"
            return f"{ticker}=X"
        return ticker

    @classmethod
    def to_fmp(cls, canonical_symbol: str) -> str:
        """
        Financial Modeling Prep (FMP) için sembol üretir.
        Örnekler:
        - 'NASDAQ:AAPL' -> 'AAPL'
        - 'BIST:THYAO' -> 'THYAO.IS'
        - 'BINANCE:BTCUSDT' -> 'BTCUSD'
        """
        exchange, ticker = cls.parse_canonical(canonical_symbol)
        if exchange == "BIST":
            return f"{ticker}.IS"
        elif exchange in ["NASDAQ", "NYSE", "AMEX"]:
            return ticker
        elif exchange == "BINANCE":
            if ticker.endswith("USDT"):
                return f"{ticker[:-4]}USD"
            return ticker
        return ticker

    @classmethod
    def to_finnhub(cls, canonical_symbol: str, asset_class: Optional[AssetClass] = None) -> str:
        """
        Finnhub için sembol üretir.
        Örnekler:
        - 'NASDAQ:AAPL' -> 'AAPL'
        - 'BINANCE:BTCUSDT' -> 'BINANCE:BTCUSDT'
        - 'FX:USDTRY' -> 'OANDA:USD_TRY'
        """
        exchange, ticker = cls.parse_canonical(canonical_symbol)
        if exchange in ["NASDAQ", "NYSE", "AMEX"]:
            return ticker
        elif exchange == "BINANCE" or asset_class == AssetClass.CRYPTO:
            return f"BINANCE:{ticker}"
        elif exchange == "FX" or asset_class == AssetClass.FOREX:
            if len(ticker) == 6:
                return f"OANDA:{ticker[:3]}_{ticker[3:]}"
            return ticker
        return ticker

    @classmethod
    def to_google_finance(cls, canonical_symbol: str, asset_class: Optional[AssetClass] = None) -> str:
        """
        Google Finance için sembol üretir.
        Örnekler:
        - 'BIST:THYAO' -> 'THYAO:IST'
        - 'NASDAQ:AAPL' -> 'AAPL:NASDAQ'
        - 'NYSE:TSLA' -> 'TSLA:NYSE'
        - 'AMEX:SPY' -> 'SPY:NYSEARCA'
        - 'BINANCE:BTCUSDT' -> 'BTC-USD'
        - 'FX:USDTRY' -> 'USD-TRY'
        - 'INDEX:DJI' -> '.DJI:INDEXDJX'
        """
        exchange, ticker = cls.parse_canonical(canonical_symbol)
        
        if exchange == "BIST":
            return f"{ticker}:IST"
        elif exchange == "NASDAQ":
            return f"{ticker}:NASDAQ"
        elif exchange == "NYSE":
            return f"{ticker}:NYSE"
        elif exchange == "AMEX":
            return f"{ticker}:NYSEARCA"
        elif exchange == "BINANCE" or asset_class == AssetClass.CRYPTO:
            if ticker.endswith("USDT"):
                return f"{ticker[:-4]}-USD"
            return ticker
        elif exchange == "FX" or asset_class == AssetClass.FOREX:
            if len(ticker) == 6:
                return f"{ticker[:3]}-{ticker[3:]}"
            return ticker
        elif exchange in ["INDEX", "TVC"]:
            if ticker == "SPX":
                return ".INX:INDEXSP"
            elif ticker == "DJI":
                return ".DJI:INDEXDJX"
            elif ticker == "NDX":
                return ".IXIC:INDEXNASDAQ"
            elif ticker == "XU100":
                return ".XU100:INDEXBIST"
        return f"{ticker}:{exchange}"

    @classmethod
    def to_tradingview(cls, canonical_symbol: str) -> str:
        """
        TradingView için sembol üretir (Kanonik sembolle doğrudan aynı).
        Örnek: 'BIST:THYAO' -> 'BIST:THYAO', 'NASDAQ:AAPL' -> 'NASDAQ:AAPL'
        """
        return canonical_symbol

    @classmethod
    def to_all_providers(cls, canonical_symbol: str, asset_class: Optional[AssetClass] = None) -> Dict[str, str]:
        """
        Tüm sağlayıcı formatlarını tek sözlükte döndürür.
        """
        return {
            "canonical": canonical_symbol,
            "isyatirim": cls.to_isyatirim(canonical_symbol),
            "yfinance": cls.to_yfinance(canonical_symbol, asset_class),
            "fmp": cls.to_fmp(canonical_symbol),
            "finnhub": cls.to_finnhub(canonical_symbol, asset_class),
            "google_finance": cls.to_google_finance(canonical_symbol, asset_class),
            "tradingview": cls.to_tradingview(canonical_symbol),
        }
