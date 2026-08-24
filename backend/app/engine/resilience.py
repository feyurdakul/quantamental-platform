"""
Finansal Dayanıklılık ve İflas Riski Modelleri (sistem_mimari.md Bölüm 7)
Altman Z-Score (5 bileşen) ve Piotroski F-Score (9 kriter) motoru.
"""

from typing import Optional, List, Dict, Any
from app.models.financials import FinancialSnapshot


class ResilienceEngine:
    """
    Altman Z-Score ve Piotroski F-Score dayanıklılık modelleri hesaplayıcısı.
    """

    @staticmethod
    def calculate_altman_z_score(snapshot: FinancialSnapshot, is_bank_or_financial: bool = False) -> Optional[float]:
        """
        Altman Z-Score (sistem_mimari.md Bölüm 7.1):
        Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E

        A = working_capital / total_assets
        B = retained_earnings / total_assets
        C = EBIT / total_assets
        D = market_cap / total_liabilities
        E = revenue / total_assets
        """
        if is_bank_or_financial:
            # Banka ve finansal kurumlarda klasik Z-Score uygulanmaz
            return None

        bs = snapshot.balance_sheet
        inc = snapshot.income_statement
        mkt = snapshot.market_context

        total_assets = bs.total_assets
        if not total_assets or total_assets <= 0:
            return None

        current_assets = bs.total_current_assets or 0
        current_liabilities = bs.total_current_liabilities or 0
        working_capital = current_assets - current_liabilities

        retained_earnings = bs.retained_earnings or 0
        ebit = inc.operating_income
        revenue = inc.revenue
        market_cap = mkt.market_cap or ((mkt.current_price * mkt.shares_outstanding) if (mkt.current_price and mkt.shares_outstanding) else None)
        total_liabilities = bs.total_liabilities or bs.total_debt

        if ebit is None or revenue is None or market_cap is None or not total_liabilities or total_liabilities <= 0:
            return None

        a = working_capital / total_assets
        b = retained_earnings / total_assets
        c = ebit / total_assets
        d = market_cap / total_liabilities
        e = revenue / total_assets

        z_score = (1.2 * a) + (1.4 * b) + (3.3 * c) + (0.6 * d) + (1.0 * e)
        return round(z_score, 2)

    @staticmethod
    def calculate_piotroski_f_score(snapshots: List[FinancialSnapshot]) -> Dict[str, Any]:
        """
        Piotroski F-Score (sistem_mimari.md Bölüm 7.2):
        9 Kriterli (0-9 Puan) Finansal Güç Skoru.
        En az iki ardışık yıllık finansal dönem gerektirir.
        """
        if len(snapshots) < 2:
            return {
                "score": None,
                "max_criteria": 9,
                "valid_criteria_count": 0,
                "status": "insufficient_data",
                "details": {}
            }

        sorted_snaps = sorted(snapshots, key=lambda s: s.period_end)
        curr = sorted_snaps[-1]
        prev = sorted_snaps[-2]

        c_inc, p_inc = curr.income_statement, prev.income_statement
        c_bs, p_bs = curr.balance_sheet, prev.balance_sheet
        c_cf, p_cf = curr.cash_flow, prev.cash_flow
        c_mkt, p_mkt = curr.market_context, prev.market_context

        score = 0
        valid_criteria = 0
        details = {}

        # --- KÂRLILIK (1 - 4) ---
        # 1. Pozitif ROA
        c_assets = c_bs.total_assets
        if c_assets and c_assets > 0 and c_inc.net_income is not None:
            c_roa = c_inc.net_income / c_assets
            details["positive_roa"] = 1 if c_roa > 0 else 0
            score += details["positive_roa"]
            valid_criteria += 1
        else:
            c_roa = None

        # 2. Pozitif Faaliyet Nakit Akışı (OCF > 0)
        if c_cf.operating_cash_flow is not None:
            details["positive_ocf"] = 1 if c_cf.operating_cash_flow > 0 else 0
            score += details["positive_ocf"]
            valid_criteria += 1

        # 3. ROA Artışı (ROA_t > ROA_(t-1))
        p_assets = p_bs.total_assets
        if c_roa is not None and p_assets and p_assets > 0 and p_inc.net_income is not None:
            p_roa = p_inc.net_income / p_assets
            details["roa_growth"] = 1 if c_roa > p_roa else 0
            score += details["roa_growth"]
            valid_criteria += 1

        # 4. Nakit Akışı Kalitesi (OCF > Net Income)
        if c_cf.operating_cash_flow is not None and c_inc.net_income is not None:
            details["ocf_over_net_income"] = 1 if c_cf.operating_cash_flow > c_inc.net_income else 0
            score += details["ocf_over_net_income"]
            valid_criteria += 1

        # --- KALDIRAÇ VE LİKİDİTE (5 - 7) ---
        # 5. Kaldıraç Azalması (Uzun Vadeli Borç veya Toplam Borç Azalması)
        c_debt = c_bs.long_term_debt or c_bs.total_debt
        p_debt = p_bs.long_term_debt or p_bs.total_debt
        if c_debt is not None and p_debt is not None:
            details["leverage_reduction"] = 1 if c_debt <= p_debt else 0
            score += details["leverage_reduction"]
            valid_criteria += 1

        # 6. Cari Oranın İyileşmesi (Current Ratio_t > Current Ratio_(t-1))
        if c_bs.total_current_assets and c_bs.total_current_liabilities and p_bs.total_current_assets and p_bs.total_current_liabilities:
            c_cr = c_bs.total_current_assets / c_bs.total_current_liabilities if c_bs.total_current_liabilities > 0 else 0
            p_cr = p_bs.total_current_assets / p_bs.total_current_liabilities if p_bs.total_current_liabilities > 0 else 0
            details["current_ratio_growth"] = 1 if c_cr > p_cr else 0
            score += details["current_ratio_growth"]
            valid_criteria += 1

        # 7. Yeni Hisse İhracı Olmaması (Seyreltilme yok)
        c_shares = c_mkt.shares_outstanding or c_inc.weighted_average_shares_diluted
        p_shares = p_mkt.shares_outstanding or p_inc.weighted_average_shares_diluted
        if c_shares is not None and p_shares is not None:
            details["no_new_shares"] = 1 if c_shares <= p_shares else 0
            score += details["no_new_shares"]
            valid_criteria += 1

        # --- OPERASYONEL VERİMLİLİK (8 - 9) ---
        # 8. Brüt Marj İyileşmesi (Gross Margin_t > Gross Margin_(t-1))
        if c_inc.gross_profit is not None and c_inc.revenue and p_inc.gross_profit is not None and p_inc.revenue:
            c_gm = c_inc.gross_profit / c_inc.revenue if c_inc.revenue > 0 else 0
            p_gm = p_inc.gross_profit / p_inc.revenue if p_inc.revenue > 0 else 0
            details["gross_margin_growth"] = 1 if c_gm > p_gm else 0
            score += details["gross_margin_growth"]
            valid_criteria += 1

        # 9. Aktif Devir Hızı İyileşmesi (Revenue / Total Assets)
        if c_inc.revenue is not None and c_assets and c_assets > 0 and p_inc.revenue is not None and p_assets and p_assets > 0:
            c_at = c_inc.revenue / c_assets
            p_at = p_inc.revenue / p_assets
            details["asset_turnover_growth"] = 1 if c_at > p_at else 0
            score += details["asset_turnover_growth"]
            valid_criteria += 1

        status = "valid" if valid_criteria >= 7 else "insufficient_data"

        return {
            "score": score if valid_criteria >= 5 else None,
            "max_criteria": 9,
            "valid_criteria_count": valid_criteria,
            "status": status,
            "details": details
        }
