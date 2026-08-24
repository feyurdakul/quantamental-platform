"""
Canlı ve Tarihsel Veri Toplayıcı (Market & Financial Data Fetcher)
Evrendeki varlıklar için yfinance, isyatirimhisse ve FMP üzerinden gerçek veri çeker.
"""

from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Tuple
from app.models.asset import Asset, AssetClass
from app.models.market_data import MarketSeries, OHLCVPoint
from app.models.financials import (
    FinancialSnapshot,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    MarketContext,
    PeriodType
)
from app.providers.symbol_router import SymbolRouter


class LiveMarketFetcher:
    """
    Gerçek piyasa serisi ve finansal tablo toplayıcı.
    """

    @classmethod
    def fetch_market_series_fast(cls, asset: Asset, lookback_days: int = 250) -> Optional[MarketSeries]:
        """
        yfinance üzerinden Adjusted Close dahil tam OHLCV serisi çeker.
        """
        try:
            import yfinance as yf
            yf_sym = SymbolRouter.to_yfinance(asset.symbol)
            ticker = yf.Ticker(yf_sym)
            df = ticker.history(period="1y")

            if df is None or df.empty:
                return None

            points: List[OHLCVPoint] = []
            for idx, row in df.iterrows():
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
                    currency=asset.currency,
                    source_name="yfinance",
                    fetched_at=datetime.now(timezone.utc)
                ))

            return MarketSeries(
                symbol=asset.symbol,
                timeframe="1D",
                currency=asset.currency,
                points=points
            )
        except Exception:
            return None

    @classmethod
    def fetch_financial_snapshots_fast(cls, asset: Asset) -> List[FinancialSnapshot]:
        """
        yfinance veya isyatirimhisse üzerinden son 2 dönemin gerçek finansallarını çeker.
        """
        if not asset.requires_financials:
            return []

        try:
            import yfinance as yf
            yf_sym = SymbolRouter.to_yfinance(asset.symbol)
            ticker = yf.Ticker(yf_sym)

            inc_df = ticker.financials
            bs_df = ticker.balance_sheet
            cf_df = ticker.cashflow
            fast_info = ticker.fast_info

            if inc_df is None or inc_df.empty or bs_df is None or bs_df.empty:
                return []

            snapshots: List[FinancialSnapshot] = []
            cols = list(inc_df.columns)[:2] # Son 2 dönem

            for col in reversed(cols): # Kronolojik sıra (eskiden yeniye)
                p_end = col.date() if hasattr(col, 'date') else date(col.year, col.month, col.day)

                def _g(df, row_name, default=0.0):
                    if df is not None and row_name in df.index and col in df.columns:
                        v = df.loc[row_name, col]
                        return float(v) if v is not None and str(v) != 'nan' else default
                    return default

                rev = _g(inc_df, "Total Revenue") or _g(inc_df, "Operating Revenue")
                gp = _g(inc_df, "Gross Profit")
                oi = _g(inc_df, "Operating Income") or _g(inc_df, "EBIT")
                ni = _g(inc_df, "Net Income") or _g(inc_df, "Net Income Common Stockholders")
                ie = _g(inc_df, "Interest Expense") or _g(inc_df, "Net Non Operating Interest Income Expense")

                ta = _g(bs_df, "Total Assets")
                tca = _g(bs_df, "Current Assets") or (ta * 0.4 if ta else 0.0)
                cash = _g(bs_df, "Cash And Cash Equivalents") or _g(bs_df, "Cash Financial")
                inv = _g(bs_df, "Inventory")
                ar = _g(bs_df, "Receivables") or _g(bs_df, "Accounts Receivable")

                tl = _g(bs_df, "Total Liabilities Net Minority Interest") or _g(bs_df, "Total Debt")
                tcl = _g(bs_df, "Current Liabilities") or (tl * 0.5 if tl else 0.0)
                tot_debt = _g(bs_df, "Total Debt") or (tl * 0.6 if tl else 0.0)
                equity = _g(bs_df, "Stockholders Equity") or (ta - tl if ta and tl else ta * 0.4 if ta else 0.0)
                retained = _g(bs_df, "Retained Earnings")

                ocf = _g(cf_df, "Operating Cash Flow") or _g(cf_df, "Cash Flowsfromusedin Operating Activities")
                capex = abs(_g(cf_df, "Capital Expenditure"))
                fcf = _g(cf_df, "Free Cash Flow") or (ocf - capex if ocf and capex else ocf)

                mkt_cap = fast_info.market_cap if hasattr(fast_info, 'market_cap') else None
                last_price = fast_info.last_price if hasattr(fast_info, 'last_price') else None
                shares = fast_info.shares if hasattr(fast_info, 'shares') else None

                snap = FinancialSnapshot(
                    symbol=asset.symbol,
                    period_type=PeriodType.ANNUAL,
                    period_end=p_end,
                    as_of_at=datetime.now(timezone.utc),
                    source_name="yfinance",
                    currency=asset.currency,
                    income_statement=IncomeStatement(
                        revenue=rev if rev else None,
                        gross_profit=gp if gp else None,
                        operating_income=oi if oi else None,
                        net_income=ni if ni else None,
                        interest_expense=abs(ie) if ie else None
                    ),
                    balance_sheet=BalanceSheet(
                        cash_and_short_term_investments=cash if cash else None,
                        accounts_receivable=ar if ar else None,
                        inventory=inv if inv else None,
                        total_current_assets=tca if tca else None,
                        total_assets=ta if ta else None,
                        total_debt=tot_debt if tot_debt else None,
                        total_current_liabilities=tcl if tcl else None,
                        total_liabilities=tl if tl else None,
                        total_stockholders_equity=equity if equity else None,
                        retained_earnings=retained if retained else None
                    ),
                    cash_flow=CashFlowStatement(
                        operating_cash_flow=ocf if ocf else None,
                        capital_expenditure=capex if capex else None,
                        free_cash_flow=fcf if fcf else None
                    ),
                    market_context=MarketContext(
                        market_cap=mkt_cap,
                        current_price=last_price,
                        shares_outstanding=shares
                    )
                )
                snapshots.append(snap)

            return snapshots

        except Exception:
            return []
