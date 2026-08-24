"""
İş Yatırım Veri Sağlayıcı Adaptörü (isyatirimhisse v5.0.1)
BIST hisseleri için resmi KAP/UFRS bilançoları, USD bazlı enflasyon arındırmalı tablolar ve banka şablonları.
"""

from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
import pandas as pd
from app.providers.base import BaseProvider
from app.providers.symbol_router import SymbolRouter
from app.models.financials import (
    FinancialSnapshot,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    MarketContext,
    PeriodType,
    SnapshotStatus
)


class IsYatirimProvider(BaseProvider):
    """
    isyatirimhisse kütüphanesini sarmalayan ve BIST finansallarını kanonik formata çeviren adaptör.
    """

    @property
    def provider_name(self) -> str:
        return "isyatirimhisse"

    def _map_row_to_financial_items(self, item_name: str, value: float, inc: IncomeStatement, bs: BalanceSheet, cf: CashFlowStatement):
        """İş Yatırım bilanço satır adlarını kanonik alanlara eşler"""
        name_lower = str(item_name).lower().strip()

        # Gelir Tablosu
        if "satış gelirleri" in name_lower or "hasılat" in name_lower or "revenue" in name_lower:
            inc.revenue = value
        elif "satışların maliyeti" in name_lower or "cost of sales" in name_lower:
            inc.cost_of_revenue = abs(value)
        elif "brüt kâr" in name_lower or "gross profit" in name_lower:
            inc.gross_profit = value
        elif "esas faaliyet kârı" in name_lower or "operating profit" in name_lower or "ebit" in name_lower:
            inc.operating_income = value
        elif "faiz giderleri" in name_lower or "finance cost" in name_lower:
            inc.interest_expense = abs(value)
        elif "vergi öncesi kâr" in name_lower:
            inc.pretax_income = value
        elif "dönem net kârı" in name_lower or "net profit" in name_lower:
            inc.net_income = value

        # Bilanço
        elif "nakit ve nakit benzerleri" in name_lower or "cash and cash equivalents" in name_lower:
            bs.cash_and_short_term_investments = value
        elif "ticari alacaklar" in name_lower:
            bs.accounts_receivable = value
        elif "stoklar" in name_lower or "inventories" in name_lower:
            bs.inventory = value
        elif "dönen varlıklar" in name_lower or "current assets" in name_lower:
            bs.total_current_assets = value
        elif "toplam varlıklar" in name_lower or "toplam aktifler" in name_lower or "total assets" in name_lower:
            bs.total_assets = value
        elif "kısa vadeli borçlanmalar" in name_lower:
            bs.short_term_debt = value
        elif "uzun vadeli borçlanmalar" in name_lower:
            bs.long_term_debt = value
        elif "ticari borçlar" in name_lower:
            bs.accounts_payable = value
        elif "kısa vadeli yükümlülükler" in name_lower or "current liabilities" in name_lower:
            bs.total_current_liabilities = value
        elif "toplam yükümlülükler" in name_lower or "toplam borçlar" in name_lower or "total liabilities" in name_lower:
            bs.total_liabilities = value
        elif "özkaynaklar" in name_lower or "ana ortaklığa ait özkaynaklar" in name_lower or "total equity" in name_lower:
            bs.total_stockholders_equity = value
        elif "geçmiş yıllar kârları" in name_lower or "retained earnings" in name_lower:
            bs.retained_earnings = value

        # Nakit Akış
        elif "işletme faaliyetlerinden nakit akışları" in name_lower:
            cf.operating_cash_flow = value
        elif "maddi ve maddi olmayan duran varlık alımı" in name_lower or "yatırım harcamaları" in name_lower:
            cf.capital_expenditure = abs(value)
        elif "ödenen temettüler" in name_lower:
            cf.dividends_paid = abs(value)

    async def fetch_financials(
        self,
        symbol: str,
        start_year: int = 2022,
        end_year: int = 2024,
        is_usd: bool = False,
        is_bank: bool = False
    ) -> List[FinancialSnapshot]:
        """
        İş Yatırım'dan BIST resmi bilançolarını çeker ve kanonik FinancialSnapshot listesine dönüştürür.
        """
        isyatirim_code = SymbolRouter.to_isyatirim(symbol)
        exchange_curr = "USD" if is_usd else "TRY"
        fin_group = "3" if is_bank else "2" # '2': UFRS (Sanayi), '3': UFRS_K (Banka/Finans)

        try:
            from isyatirimhisse import fetch_financials as isy_fetch
            df = isy_fetch(
                symbols=isyatirim_code,
                start_year=start_year,
                end_year=end_year,
                exchange=exchange_curr,
                financial_group=fin_group,
                save_to_excel=False
            )
            
            if df is None or df.empty:
                return []

            # df sütunları: Bilanço kalemleri satır, dönemler sütun şeklindedir (örn: '2023/12', '2024/12' vb.)
            snapshots: List[FinancialSnapshot] = []
            period_cols = [c for c in df.columns if "/" in str(c)]
            
            for p_col in period_cols:
                parts = str(p_col).split("/")
                if len(parts) != 2:
                    continue
                year, month = int(parts[0]), int(parts[1])
                # Ay sonu tarihi oluşturma
                p_end = date(year, month, 28 if month == 2 else 30 if month in [4, 6, 9, 11] else 31)
                
                inc = IncomeStatement()
                bs = BalanceSheet()
                cf = CashFlowStatement()
                
                for _, row in df.iterrows():
                    item_name = row.iloc[0] if len(row) > 0 else ""
                    val = row.get(p_col)
                    if pd.notna(val) and isinstance(val, (int, float)):
                        self._map_row_to_financial_items(item_name, float(val), inc, bs, cf)

                # Toplam borç hesabı (short + long)
                if bs.total_debt is None and (bs.short_term_debt or bs.long_term_debt):
                    bs.total_debt = (bs.short_term_debt or 0) + (bs.long_term_debt or 0)

                # Serbest Nakit Akışı (FCF = OCF - Capex)
                if cf.free_cash_flow is None and cf.operating_cash_flow is not None and cf.capital_expenditure is not None:
                    cf.free_cash_flow = cf.operating_cash_flow - cf.capital_expenditure

                snapshot = FinancialSnapshot(
                    symbol=symbol,
                    period_type=PeriodType.ANNUAL if month == 12 else PeriodType.QUARTERLY,
                    period_end=p_end,
                    as_of_at=datetime.now(timezone.utc),
                    source_name=self.provider_name,
                    source_endpoint="fetch_financials",
                    currency=exchange_curr,
                    is_usd_converted=is_usd,
                    comparability_limited=(not is_usd), # TRY bilançoları TMS-29 kısıtı taşır
                    income_statement=inc,
                    balance_sheet=bs,
                    cash_flow=cf,
                    market_context=MarketContext()
                )
                snapshots.append(snapshot)

            return snapshots

        except Exception as e:
            # Hata durumunda boş liste döner, uygulama çökmez
            return []
