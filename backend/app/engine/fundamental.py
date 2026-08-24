"""
Temel Analiz ve Finansal Oran Hesaplama Motoru (sistem_mimari.md Bölüm 6)
Değerleme, Kârlılık, Büyüme, Likidite, Borçluluk, Faiz Karşılama ve Nakit Döngüsü metriklerini hesaplar.
"""

from typing import Dict, Optional, List, Any
from app.models.financials import FinancialSnapshot


class FundamentalEngine:
    """
    Kanonik FinancialSnapshot verisi üzerinden finansal oranları ve büyüme metriklerini hesaplar.
    """

    @staticmethod
    def calculate_valuation_metrics(snapshot: FinancialSnapshot) -> Dict[str, Any]:
        """
        Değerleme Oranları (sistem_mimari.md Bölüm 6.1):
        F/K, PD/DD, FD/FAVÖK, FCF Verimi, Kazanç Verimi
        """
        inc = snapshot.income_statement
        bs = snapshot.balance_sheet
        cf = snapshot.cash_flow
        mkt = snapshot.market_context

        price = mkt.current_price
        market_cap = mkt.market_cap or (price * mkt.shares_outstanding if (price and mkt.shares_outstanding) else None)
        net_income = inc.net_income
        eps = inc.eps_diluted
        equity = bs.total_stockholders_equity
        ebitda = inc.ebitda
        total_debt = bs.total_debt or ((bs.short_term_debt or 0) + (bs.long_term_debt or 0))
        cash = bs.cash_and_short_term_investments or 0
        fcf = cf.free_cash_flow or (
            (cf.operating_cash_flow - cf.capital_expenditure)
            if (cf.operating_cash_flow is not None and cf.capital_expenditure is not None)
            else None
        )

        # Firma Değeri (EV) = Market Cap + Total Debt - Cash
        enterprise_value = mkt.enterprise_value or (
            (market_cap + total_debt - cash)
            if (market_cap is not None and total_debt is not None)
            else None
        )

        # F/K (P/E Ratio)
        pe_ratio = None
        if price and eps and eps > 0:
            pe_ratio = price / eps
        elif market_cap and net_income and net_income > 0:
            pe_ratio = market_cap / net_income

        # PD/DD (P/B Ratio)
        pb_ratio = None
        if market_cap and equity and equity > 0:
            pb_ratio = market_cap / equity
        elif price and equity and mkt.shares_outstanding and mkt.shares_outstanding > 0:
            book_value_per_share = equity / mkt.shares_outstanding
            if book_value_per_share > 0:
                pb_ratio = price / book_value_per_share

        # FD/FAVÖK (EV/EBITDA)
        ev_ebitda = None
        if enterprise_value and ebitda and ebitda > 0:
            ev_ebitda = enterprise_value / ebitda

        # FCF Verimi (FCF / Market Cap)
        fcf_yield = None
        if fcf and market_cap and market_cap > 0:
            fcf_yield = fcf / market_cap

        # Kazanç Verimi (Earnings Yield = Net Income / Market Cap = 1 / P/E)
        earnings_yield = None
        if net_income and market_cap and market_cap > 0:
            earnings_yield = net_income / market_cap

        return {
            "market_cap": market_cap,
            "enterprise_value": enterprise_value,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
            "pb_ratio": round(pb_ratio, 2) if pb_ratio else None,
            "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None,
            "fcf_yield": round(fcf_yield, 4) if fcf_yield else None,
            "earnings_yield": round(earnings_yield, 4) if earnings_yield else None,
            "free_cash_flow": fcf
        }

    @staticmethod
    def calculate_quality_metrics(snapshot: FinancialSnapshot, previous_snapshot: Optional[FinancialSnapshot] = None) -> Dict[str, Any]:
        """
        Kalite ve Kârlılık Oranları (sistem_mimari.md Bölüm 6.2):
        ROE, ROA, Faaliyet Marjı, Net Kâr Marjı, Brüt Marj, ROIC
        """
        inc = snapshot.income_statement
        bs = snapshot.balance_sheet

        revenue = inc.revenue
        net_income = inc.net_income
        operating_income = inc.operating_income
        gross_profit = inc.gross_profit
        equity = bs.total_stockholders_equity
        total_assets = bs.total_assets

        # Ortalama bilanço kalemleri (önceki dönem varsa)
        avg_equity = (
            (equity + previous_snapshot.balance_sheet.total_stockholders_equity) / 2.0
            if (previous_snapshot and previous_snapshot.balance_sheet.total_stockholders_equity and equity)
            else equity
        )
        avg_assets = (
            (total_assets + previous_snapshot.balance_sheet.total_assets) / 2.0
            if (previous_snapshot and previous_snapshot.balance_sheet.total_assets and total_assets)
            else total_assets
        )

        # ROE (Net Income / Equity)
        roe = (net_income / avg_equity) if (net_income is not None and avg_equity and avg_equity > 0) else None

        # ROA (Net Income / Assets)
        roa = (net_income / avg_assets) if (net_income is not None and avg_assets and avg_assets > 0) else None

        # Marjlar
        operating_margin = (operating_income / revenue) if (operating_income is not None and revenue and revenue > 0) else None
        net_margin = (net_income / revenue) if (net_income is not None and revenue and revenue > 0) else None
        gross_margin = (gross_profit / revenue) if (gross_profit is not None and revenue and revenue > 0) else None

        # ROIC = NOPAT / Invested Capital
        # NOPAT = EBIT * (1 - Tax Rate), Invested Capital = Total Debt + Equity - Cash
        roic = None
        if operating_income and bs.total_stockholders_equity:
            tax_rate = 0.25 # Varsayılan efektif vergi oranı
            if inc.pretax_income and inc.income_tax_expense and inc.pretax_income > 0:
                tax_rate = max(0.0, min(0.40, inc.income_tax_expense / inc.pretax_income))
            nopat = operating_income * (1.0 - tax_rate)
            total_debt = bs.total_debt or ((bs.short_term_debt or 0) + (bs.long_term_debt or 0)) or 0
            cash = bs.cash_and_short_term_investments or 0
            invested_cap = total_debt + bs.total_stockholders_equity - cash
            if invested_cap > 0:
                roic = nopat / invested_cap

        return {
            "roe": round(roe, 4) if roe is not None else None,
            "roa": round(roa, 4) if roa is not None else None,
            "operating_margin": round(operating_margin, 4) if operating_margin is not None else None,
            "net_margin": round(net_margin, 4) if net_margin is not None else None,
            "gross_margin": round(gross_margin, 4) if gross_margin is not None else None,
            "roic": round(roic, 4) if roic is not None else None
        }

    @staticmethod
    def calculate_growth_metrics(snapshots: List[FinancialSnapshot]) -> Dict[str, Any]:
        """
        Büyüme Oranları (sistem_mimari.md Bölüm 6.3):
        Gelir, Net Kâr, EPS ve FCF Büyümeleri
        """
        if len(snapshots) < 2:
            return {
                "revenue_growth": None,
                "net_income_growth": None,
                "eps_growth": None,
                "fcf_growth": None,
                "base_effect_warning": False
            }

        # Kronolojik sıralama: en eski [0], en güncel [-1]
        sorted_snaps = sorted(snapshots, key=lambda s: s.period_end)
        curr = sorted_snaps[-1]
        prev = sorted_snaps[-2]

        def pct_change(c_val: Optional[float], p_val: Optional[float]) -> tuple[Optional[float], bool]:
            if c_val is None or p_val is None or p_val == 0:
                return None, False
            # Negatiften pozitife geçişte baz etkisi uyarısı
            base_effect = (p_val < 0 and c_val > 0) or (abs(p_val) < 1000)
            if p_val < 0:
                return (c_val - p_val) / abs(p_val), True
            return (c_val / p_val) - 1.0, base_effect

        rev_g, rev_warn = pct_change(curr.income_statement.revenue, prev.income_statement.revenue)
        ni_g, ni_warn = pct_change(curr.income_statement.net_income, prev.income_statement.net_income)
        eps_g, eps_warn = pct_change(curr.income_statement.eps_diluted, prev.income_statement.eps_diluted)
        
        curr_fcf = curr.cash_flow.free_cash_flow
        prev_fcf = prev.cash_flow.free_cash_flow
        fcf_g, fcf_warn = pct_change(curr_fcf, prev_fcf)

        return {
            "revenue_growth": round(rev_g, 4) if rev_g is not None else None,
            "net_income_growth": round(ni_g, 4) if ni_g is not None else None,
            "eps_growth": round(eps_g, 4) if eps_g is not None else None,
            "fcf_growth": round(fcf_g, 4) if fcf_g is not None else None,
            "base_effect_warning": (rev_warn or ni_warn or eps_warn or fcf_warn)
        }

    @staticmethod
    def calculate_liquidity_and_leverage_metrics(snapshot: FinancialSnapshot) -> Dict[str, Any]:
        """
        Likidite, Borçluluk ve Faiz Karşılama Oranları (sistem_mimari.md Bölüm 6.4, 6.5, 6.6):
        Cari Oran, Asit-Test, Net Borç / Özsermaye, Faiz Karşılama
        """
        bs = snapshot.balance_sheet
        inc = snapshot.income_statement

        current_assets = bs.total_current_assets
        current_liabilities = bs.total_current_liabilities
        cash = bs.cash_and_short_term_investments or 0
        receivables = bs.accounts_receivable or 0
        inventory = bs.inventory or 0
        total_debt = bs.total_debt or ((bs.short_term_debt or 0) + (bs.long_term_debt or 0))
        equity = bs.total_stockholders_equity
        total_liabilities = bs.total_liabilities
        ebit = inc.operating_income
        interest_exp = inc.interest_expense

        # Cari Oran (Current Ratio)
        current_ratio = (current_assets / current_liabilities) if (current_assets and current_liabilities and current_liabilities > 0) else None

        # Asit-Test Oranı (Quick Ratio) = (Current Assets - Inventory) / Current Liabilities
        quick_ratio = None
        if current_assets and current_liabilities and current_liabilities > 0:
            quick_ratio = (current_assets - inventory) / current_liabilities

        # Net İşletme Sermayesi (NWC)
        net_working_capital = (current_assets - current_liabilities) if (current_assets and current_liabilities) else None

        # Net Borç = Total Debt - Cash
        net_debt = (total_debt - cash) if total_debt is not None else None
        
        # Net Borç / Özsermaye (Net Debt to Equity)
        net_debt_to_equity = None
        if net_debt is not None and equity:
            net_debt_to_equity = net_debt / equity

        # Brüt Borç / Özsermaye Teşhisi (sistem_mimari.md Bölüm 6.5)
        gross_debt_to_equity = (total_debt / equity) if (total_debt is not None and equity and equity > 0) else None
        liabilities_to_equity = (total_liabilities / equity) if (total_liabilities and equity and equity > 0) else None

        # Faiz Karşılama Oranı (Interest Coverage) = EBIT / abs(Interest Expense)
        interest_coverage = None
        if ebit is not None and interest_exp and abs(interest_exp) > 0:
            interest_coverage = ebit / abs(interest_exp)

        flags = []
        if liabilities_to_equity and liabilities_to_equity > 5.0:
            flags.append("HIGH_TOTAL_LIABILITIES")
        if gross_debt_to_equity and gross_debt_to_equity > 4.0:
            flags.append("HIGH_GROSS_DEBT")

        return {
            "current_ratio": round(current_ratio, 2) if current_ratio else None,
            "quick_ratio": round(quick_ratio, 2) if quick_ratio else None,
            "net_working_capital": net_working_capital,
            "net_debt": net_debt,
            "net_debt_to_equity": round(net_debt_to_equity, 2) if net_debt_to_equity is not None else None,
            "gross_debt_to_equity": round(gross_debt_to_equity, 2) if gross_debt_to_equity else None,
            "liabilities_to_equity": round(liabilities_to_equity, 2) if liabilities_to_equity else None,
            "interest_coverage": round(interest_coverage, 2) if interest_coverage else None,
            "flags": flags
        }
