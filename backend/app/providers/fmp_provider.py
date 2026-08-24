"""
Financial Modeling Prep (FMP) Veri Sağlayıcı Adaptörü
ABD hisseleri için standartlaştırılmış GAAP/IFRS 3 finansal tablo ve Firma Değeri (EV).
"""

from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
import httpx
from app.providers.base import BaseProvider
from app.providers.symbol_router import SymbolRouter
from app.models.financials import (
    FinancialSnapshot,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    MarketContext,
    PeriodType
)


class FMPProvider(BaseProvider):
    """
    FMP REST API Adaptörü.
    """

    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"

    @property
    def provider_name(self) -> str:
        return "FMP"

    async def fetch_financials(self, symbol: str, years: int = 4, is_usd: bool = True) -> List[FinancialSnapshot]:
        """
        FMP'den yıllık Income, Balance Sheet ve Cash Flow tablolarını çeker.
        """
        fmp_symbol = SymbolRouter.to_fmp(symbol)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # 1. Income Statement
                r_inc = await client.get(f"{self.base_url}/income-statement/{fmp_symbol}?limit={years}&apikey={self.api_key}")
                data_inc = r_inc.json() if r_inc.status_code == 200 else []

                # 2. Balance Sheet
                r_bs = await client.get(f"{self.base_url}/balance-sheet-statement/{fmp_symbol}?limit={years}&apikey={self.api_key}")
                data_bs = r_bs.json() if r_bs.status_code == 200 else []

                # 3. Cash Flow
                r_cf = await client.get(f"{self.base_url}/cash-flow-statement/{fmp_symbol}?limit={years}&apikey={self.api_key}")
                data_cf = r_cf.json() if r_cf.status_code == 200 else []

                # 4. Enterprise Values
                r_ev = await client.get(f"{self.base_url}/enterprise-values/{fmp_symbol}?limit={years}&apikey={self.api_key}")
                data_ev = r_ev.json() if r_ev.status_code == 200 else []

                if not isinstance(data_inc, list) or len(data_inc) == 0:
                    return []

                # Tarihlere göre eşleştirme
                bs_map = {item.get("date"): item for item in data_bs if isinstance(item, dict)}
                cf_map = {item.get("date"): item for item in data_cf if isinstance(item, dict)}
                ev_map = {item.get("date"): item for item in data_ev if isinstance(item, dict)}

                snapshots: List[FinancialSnapshot] = []
                for inc_item in data_inc:
                    d_str = inc_item.get("date")
                    if not d_str:
                        continue
                    p_end = date.fromisoformat(d_str)
                    
                    bs_item = bs_map.get(d_str, {})
                    cf_item = cf_map.get(d_str, {})
                    ev_item = ev_map.get(d_str, {})

                    inc = IncomeStatement(
                        revenue=inc_item.get("revenue"),
                        cost_of_revenue=inc_item.get("costOfRevenue"),
                        gross_profit=inc_item.get("grossProfit"),
                        operating_income=inc_item.get("operatingIncome"),
                        ebitda=inc_item.get("ebitda"),
                        interest_expense=inc_item.get("interestExpense"),
                        pretax_income=inc_item.get("incomeBeforeTax"),
                        income_tax_expense=inc_item.get("incomeTaxExpense"),
                        net_income=inc_item.get("netIncome"),
                        eps_diluted=inc_item.get("epsdiluted"),
                        weighted_average_shares_diluted=inc_item.get("weightedAverageShsOutDil")
                    )

                    bs = BalanceSheet(
                        cash_and_short_term_investments=bs_item.get("cashAndShortTermInvestments"),
                        accounts_receivable=bs_item.get("netReceivables"),
                        inventory=bs_item.get("inventory"),
                        total_current_assets=bs_item.get("totalCurrentAssets"),
                        total_assets=bs_item.get("totalAssets"),
                        short_term_debt=bs_item.get("shortTermDebt"),
                        long_term_debt=bs_item.get("longTermDebt"),
                        total_debt=bs_item.get("totalDebt"),
                        accounts_payable=bs_item.get("accountPayables"),
                        total_current_liabilities=bs_item.get("totalCurrentLiabilities"),
                        total_liabilities=bs_item.get("totalLiabilities"),
                        total_stockholders_equity=bs_item.get("totalStockholdersEquity"),
                        retained_earnings=bs_item.get("retainedEarnings")
                    )

                    cf = CashFlowStatement(
                        operating_cash_flow=cf_item.get("operatingCashFlow"),
                        capital_expenditure=cf_item.get("capitalExpenditure"),
                        free_cash_flow=cf_item.get("freeCashFlow"),
                        depreciation_and_amortization=cf_item.get("depreciationAndAmortization"),
                        share_issuance_or_repurchase=cf_item.get("commonStockRepurchased"),
                        dividends_paid=cf_item.get("dividendsPaid")
                    )

                    mkt = MarketContext(
                        market_cap=ev_item.get("marketCap"),
                        enterprise_value=ev_item.get("enterpriseValue"),
                        shares_outstanding=ev_item.get("numberOfShares"),
                        current_price=ev_item.get("stockPrice")
                    )

                    snap = FinancialSnapshot(
                        symbol=symbol,
                        period_type=PeriodType.ANNUAL,
                        period_end=p_end,
                        as_of_at=datetime.now(timezone.utc),
                        source_name=self.provider_name,
                        source_endpoint="statements",
                        currency=inc_item.get("reportedCurrency", "USD"),
                        income_statement=inc,
                        balance_sheet=bs,
                        cash_flow=cf,
                        market_context=mkt
                    )
                    snapshots.append(snap)

                return snapshots

            except Exception:
                return []
