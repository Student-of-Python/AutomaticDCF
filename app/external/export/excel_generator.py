"""
app/external/export/excel_generator.py

Generates executive-grade multi-sheet Excel valuation reports (.xlsx)
for the Discounted Cash Flow (DCF) Valuation Engine.
"""
from __future__ import annotations
import io
from datetime import datetime
from typing import Sequence, Any

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.application.dto import CalculateDCFResponse, CalculateDCFRequest
from app.domain.enums import IncomeStatementCols, CashStatementCols, BalanceSheetCols


class ExcelReportGenerator:
    """
    Renders a comprehensive, institutional-grade Excel model for a DCF valuation.
    Produces 3 formatted sheets:
      1. Valuation Summary & DCF Model (Bridge, FCFF Schedule, Terminal Value)
      2. Historical Financials (Income Statement, Cash Flow, Balance Sheet)
      3. WACC & Macro Assumptions (CAPM, Cost of Debt, Capital Structure)
    """

    # Palette
    NAVY_DARK = "0E1E38"
    NAVY_MED = "1A3358"
    NAVY_LIGHT = "264674"
    BRASS = "B08D3C"
    BRASS_LIGHT = "FBF7EC"
    PAPER = "F4F6F9"
    SHEET_WHITE = "FFFFFF"
    RULE_BORDER = "DDE1E8"
    GAIN_GREEN = "137752"
    LOSS_RED = "AD3428"
    TEXT_MUTED = "6B778A"
    TEXT_DARK = "12233F"

    FONT_FAMILY = "Segoe UI"

    @classmethod
    def generate(
        cls,
        response: CalculateDCFResponse,
        request: CalculateDCFRequest | None = None
    ) -> bytes:
        wb = openpyxl.Workbook()

        # Sheet 1: Valuation Summary & DCF Model
        ws_model = wb.active
        ws_model.title = "DCF Valuation Model"
        cls._build_model_sheet(ws_model, response, request)

        # Sheet 2: Historical Financials
        ws_hist = wb.create_sheet(title="Historical Financials")
        cls._build_historical_sheet(ws_hist, response)

        # Sheet 3: WACC & Macro Framework
        ws_wacc = wb.create_sheet(title="WACC & Assumptions")
        cls._build_wacc_sheet(ws_wacc, response, request)

        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    # -------------------------------------------------------------------------
    # Styling Helpers
    # -------------------------------------------------------------------------
    @classmethod
    def _border_all(cls, color: str = RULE_BORDER, style: str = "thin") -> Border:
        s = Side(border_style=style, color=color)
        return Border(left=s, right=s, top=s, bottom=s)

    @classmethod
    def _border_top_bottom(cls, top_style: str = "thin", bottom_style: str = "double") -> Border:
        return Border(
            top=Side(border_style=top_style, color=cls.RULE_BORDER),
            bottom=Side(border_style=bottom_style, color=cls.NAVY_DARK)
        )

    @classmethod
    def _style_header_banner(
        cls,
        ws,
        title: str,
        subtitle: str,
        max_col: int = 7
    ) -> None:
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_col)
        cell_title = ws.cell(row=1, column=1, value=title)
        cell_title.font = Font(name=cls.FONT_FAMILY, size=15, bold=True, color="FFFFFF")
        cell_title.fill = PatternFill(start_color=cls.NAVY_DARK, end_color=cls.NAVY_DARK, fill_type="solid")
        cell_title.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[1].height = 36

        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max_col)
        cell_sub = ws.cell(row=2, column=1, value=subtitle)
        cell_sub.font = Font(name=cls.FONT_FAMILY, size=9, bold=False, color="DBE3F0")
        cell_sub.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        cell_sub.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[2].height = 22
        ws.row_dimensions[3].height = 14  # spacer row

    @classmethod
    def _auto_fit_columns(cls, ws, min_width: int = 14) -> None:
        ws.views.sheetView[0].showGridLines = True
        for col in ws.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = 0
            for cell in col:
                # ignore merged header rows 1 & 2 for width calculation
                if cell.row in (1, 2):
                    continue
                val = str(cell.value or "")
                if len(val) > max_len:
                    max_len = len(val)
            pad = 6 if col[0].column == 1 else 4
            ws.column_dimensions[col_letter].width = max(max_len + pad, min_width)

    # -------------------------------------------------------------------------
    # Sheet 1: DCF Valuation Model
    # -------------------------------------------------------------------------
    @classmethod
    def _build_model_sheet(
        cls,
        ws,
        resp: CalculateDCFResponse,
        req: CalculateDCFRequest | None
    ) -> None:
        n_years = len(resp.schedule.fcff)
        max_col = max(7, n_years + 2)

        verdict = "UNDERVALUED" if resp.upside_downside_pct >= 0 else "OVERVALUED"
        subtitle = (
            f"Ticker: {resp.ticker}   |   Current Price: ${resp.current_price:,.2f}   |   "
            f"Implied DCF Value: ${resp.implied_share_price:,.2f}   |   "
            f"Spread: {resp.upside_downside_pct:+.1%} ({verdict})   |   "
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        cls._style_header_banner(ws, "DISCOUNTED CASH FLOW (DCF) INTRINSIC VALUATION MODEL", subtitle, max_col)

        # Row 4: Valuation Bridge Section Header
        r = 4
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        c = ws.cell(row=r, column=1, value="1. ENTERPRISE TO EQUITY VALUE BRIDGE")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        bridge_headers = ["Valuation Bridge Line Item", "Amount ($)", "% of Enterprise Value"]
        for col_idx, h in enumerate(bridge_headers, start=1):
            cell = ws.cell(row=r, column=col_idx, value=h)
            cell.font = Font(name=cls.FONT_FAMILY, size=10, bold=True, color=cls.NAVY_DARK)
            cell.fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
            cell.border = cls._border_all()
            if col_idx > 1:
                cell.alignment = Alignment(horizontal="right")
        r += 1

        bridge_rows = [
            ("PV of Explicit Forecast Cash Flows (Horizon)", resp.pv_fcff, resp.pv_fcff / resp.enterprise_value if resp.enterprise_value else 0),
            ("PV of Terminal Perpetuity / Exit Value", resp.pv_terminal_value, resp.pv_terminal_value / resp.enterprise_value if resp.enterprise_value else 0),
            ("Total Enterprise Value (EV)", resp.enterprise_value, 1.0),
            ("Less: Total Debt Obligations", resp.total_debt, None),
            ("Plus: Cash & Liquid Equivalents", resp.cash, None),
            ("Implied Equity Value", resp.equity_value, None),
            ("Diluted Shares Outstanding", resp.shares_outstanding, None),
            ("Implied DCF Fair Value per Share", resp.implied_share_price, None),
            ("Current Market Price per Share", resp.current_price, None),
            ("Implied Margin of Safety / (Discount)", resp.upside_downside_pct, None),
        ]

        for item, val, pct in bridge_rows:
            is_bold = item in ("Total Enterprise Value (EV)", "Implied Equity Value", "Implied DCF Fair Value per Share")
            is_gold = item == "Implied DCF Fair Value per Share"
            is_spread = "Margin of Safety" in item

            c1 = ws.cell(row=r, column=1, value=item)
            c2 = ws.cell(row=r, column=2, value=val)
            c3 = ws.cell(row=r, column=3, value=pct if pct is not None else "-")

            for c in (c1, c2, c3):
                c.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold, color=cls.NAVY_DARK)
                c.border = cls._border_all()

            if is_gold:
                for c in (c1, c2, c3):
                    c.fill = PatternFill(start_color=cls.BRASS_LIGHT, end_color=cls.BRASS_LIGHT, fill_type="solid")
                    c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color=cls.NAVY_DARK)

            # Format Column 2
            c2.alignment = Alignment(horizontal="right")
            if is_spread:
                c2.number_format = "+0.0%;-0.0%"
                color = cls.GAIN_GREEN if val >= 0 else cls.LOSS_RED
                c2.font = Font(name=cls.FONT_FAMILY, size=10, bold=True, color=color)
            elif item == "Diluted Shares Outstanding":
                c2.number_format = "#,##0"
            elif "per Share" in item or "Price" in item:
                c2.number_format = "$#,##0.00"
            else:
                c2.number_format = "$#,##0"

            # Format Column 3
            c3.alignment = Alignment(horizontal="right")
            if pct is not None:
                c3.number_format = "0.0%"

            r += 1

        # Spacer
        r += 1

        # Row: Explicit Cash Flow Schedule
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=n_years + 1)
        c = ws.cell(row=r, column=1, value="2. PROJECTED FREE CASH FLOW TO FIRM (FCFF) SCHEDULE")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        # Table Header
        h_cell = ws.cell(row=r, column=1, value="Cash Flow Driver / Metric")
        h_cell.font = Font(name=cls.FONT_FAMILY, size=10, bold=True, color=cls.NAVY_DARK)
        h_cell.fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
        h_cell.border = cls._border_all()

        for yr in range(1, n_years + 1):
            cell = ws.cell(row=r, column=yr + 1, value=f"Year {yr}")
            cell.font = Font(name=cls.FONT_FAMILY, size=10, bold=True, color=cls.NAVY_DARK)
            cell.fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
            cell.alignment = Alignment(horizontal="right")
            cell.border = cls._border_all()
        r += 1

        # Line items
        sched = resp.schedule
        tax = resp.tax_rate

        schedule_data = [
            ("Projected Revenue", sched.revenues, "$#,##0", False, None),
            ("Operating Profit (EBIT)", sched.ebits, "$#,##0", False, None),
            ("Effective Corporate Tax Rate", [tax] * n_years, "0.0%", False, None),
            ("Net Operating Profit After Tax (NOPAT)", sched.nopats, "$#,##0", False, None),
            ("(+) Depreciation & Amortization (D&A)", sched.da, "$#,##0", False, None),
            ("(-) Capital Expenditures (CapEx)", sched.capex, "$#,##0", False, None),
            ("(-) Net Working Capital Investment (Delta NWC)", sched.delta_nwc, "$#,##0", False, None),
            ("Unlevered Free Cash Flow (FCFF)", sched.fcff, "$#,##0", True, cls.PAPER),
        ]

        for label, series, fmt, is_bold, fill_color in schedule_data:
            c_label = ws.cell(row=r, column=1, value=label)
            c_label.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold, color=cls.NAVY_DARK)
            c_label.border = cls._border_all()
            if fill_color:
                c_label.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

            for idx, val in enumerate(series, start=1):
                c_val = ws.cell(row=r, column=idx + 1, value=val)
                c_val.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold, color=cls.NAVY_DARK)
                c_val.alignment = Alignment(horizontal="right")
                c_val.number_format = fmt
                c_val.border = cls._border_all()
                if fill_color:
                    c_val.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
            r += 1

        # Discounting rows
        wacc = resp.wacc
        discount_factors = [1.0 / ((1.0 + wacc) ** t) for t in range(1, n_years + 1)]
        pv_fcffs = [cf * df for cf, df in zip(sched.fcff, discount_factors)]

        c_t = ws.cell(row=r, column=1, value="Discount Period (t)")
        c_t.font = Font(name=cls.FONT_FAMILY, size=9, italic=True)
        c_t.border = cls._border_all()
        for idx in range(1, n_years + 1):
            c = ws.cell(row=r, column=idx + 1, value=idx)
            c.alignment = Alignment(horizontal="right")
            c.font = Font(name=cls.FONT_FAMILY, size=9, italic=True)
            c.border = cls._border_all()
        r += 1

        c_df = ws.cell(row=r, column=1, value="Discount Factor [1 / (1 + WACC)^t]")
        c_df.font = Font(name=cls.FONT_FAMILY, size=9, italic=True)
        c_df.border = cls._border_all()
        for idx, df in enumerate(discount_factors, start=1):
            c = ws.cell(row=r, column=idx + 1, value=df)
            c.alignment = Alignment(horizontal="right")
            c.number_format = "0.0000"
            c.font = Font(name=cls.FONT_FAMILY, size=9, italic=True)
            c.border = cls._border_all()
        r += 1

        c_pv = ws.cell(row=r, column=1, value="Present Value of FCFF (PV)")
        c_pv.font = Font(name=cls.FONT_FAMILY, size=10, bold=True, color=cls.NAVY_DARK)
        c_pv.fill = PatternFill(start_color=cls.BRASS_LIGHT, end_color=cls.BRASS_LIGHT, fill_type="solid")
        c_pv.border = cls._border_all()
        for idx, pv in enumerate(pv_fcffs, start=1):
            c = ws.cell(row=r, column=idx + 1, value=pv)
            c.alignment = Alignment(horizontal="right")
            c.number_format = "$#,##0"
            c.font = Font(name=cls.FONT_FAMILY, size=10, bold=True, color=cls.NAVY_DARK)
            c.fill = PatternFill(start_color=cls.BRASS_LIGHT, end_color=cls.BRASS_LIGHT, fill_type="solid")
            c.border = cls._border_all()
        r += 1

        # Spacer
        r += 1

        # Row: Terminal Value Specification
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        c = ws.cell(row=r, column=1, value="3. TERMINAL VALUE PARAMETERS")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        is_multiple = resp.exit_multiple is not None
        method_name = f"Exit Multiple ({resp.exit_multiple:.1f}x EBITDA)" if is_multiple else f"Gordon Growth ({resp.terminal_growth_rate:.1%})"
        undisc_tv = resp.pv_terminal_value * ((1 + wacc) ** n_years)

        tv_specs = [
            ("Terminal Value Methodology", method_name, "@"),
            ("Terminal Growth Rate (g)", resp.terminal_growth_rate, "0.0%"),
            ("Exit Multiple (EV / EBITDA)", resp.exit_multiple if is_multiple else "N/A", "0.0x" if is_multiple else "@"),
            ("Terminal Year EBITDA", sched.terminal_ebitda, "$#,##0"),
            ("Undiscounted Terminal Value (Year N)", undisc_tv, "$#,##0"),
            ("Discount Factor to Present", 1.0 / ((1 + wacc) ** n_years), "0.0000"),
            ("Present Value of Terminal Value (PV TV)", resp.pv_terminal_value, "$#,##0"),
            ("Terminal Value % of Enterprise Value", resp.pv_terminal_value / resp.enterprise_value if resp.enterprise_value else 0, "0.0%"),
        ]

        for label, val, fmt in tv_specs:
            c1 = ws.cell(row=r, column=1, value=label)
            c2 = ws.cell(row=r, column=2, value=val)
            c1.font = Font(name=cls.FONT_FAMILY, size=10, bold=("PV TV" in label or "Methodology" in label))
            c2.font = Font(name=cls.FONT_FAMILY, size=10, bold=("PV TV" in label or "Methodology" in label))
            c1.border = cls._border_all()
            c2.border = cls._border_all()
            c2.alignment = Alignment(horizontal="right")
            if fmt != "@":
                c2.number_format = fmt
            r += 1

        cls._auto_fit_columns(ws, min_width=16)

    # -------------------------------------------------------------------------
    # Sheet 2: Historical Financials
    # -------------------------------------------------------------------------
    @classmethod
    def _build_historical_sheet(cls, ws, resp: CalculateDCFResponse) -> None:
        st = resp.historical_statements
        max_col = 6
        if st is not None and not st.income.empty:
            max_col = max(max_col, len(st.income.index) + 1)

        subtitle = f"Company: {resp.ticker}   |   Historical Financial Accounting Statements & Operating Ratios"
        cls._style_header_banner(ws, "HISTORICAL FINANCIAL STATEMENTS (STANDARDIZED)", subtitle, max_col)

        if st is None or st.income.empty:
            ws.cell(row=4, column=1, value="Historical financial statement data not available for this ticker.")
            cls._auto_fit_columns(ws)
            return

        dates = [d.strftime("%Y-%m") if hasattr(d, "strftime") else str(d) for d in st.income.index]
        n_periods = len(dates)

        r = 4
        # Section A: Income Statement
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=n_periods + 1)
        c = ws.cell(row=r, column=1, value="INCOME STATEMENT LINE ITEMS")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        # Header row
        ws.cell(row=r, column=1, value="Metric ($ in nominal terms)").fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
        ws.cell(row=r, column=1).font = Font(name=cls.FONT_FAMILY, size=10, bold=True)
        ws.cell(row=r, column=1).border = cls._border_all()

        for idx, dt in enumerate(dates, start=1):
            cell = ws.cell(row=r, column=idx + 1, value=f"FY {dt}")
            cell.font = Font(name=cls.FONT_FAMILY, size=10, bold=True)
            cell.fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
            cell.alignment = Alignment(horizontal="right")
            cell.border = cls._border_all()
        r += 1

        inc = st.income
        inc_rows = [
            ("Total Revenues", inc[IncomeStatementCols.REVENUE], "$#,##0", True),
            ("Operating Profitability (EBITDA)", inc[IncomeStatementCols.EBITDA], "$#,##0", False),
            ("Operating Income (EBIT)", inc[IncomeStatementCols.EBIT], "$#,##0", True),
            ("Pre-Tax Income (EBT)", inc[IncomeStatementCols.PRETAX_INCOME], "$#,##0", False),
            ("Income Tax Expense", inc[IncomeStatementCols.INCOME_TAX_EXPENSE], "$#,##0", False),
            ("Interest & Debt Expense", inc[IncomeStatementCols.INTEREST_EXPENSE], "$#,##0", False),
        ]

        for label, series, fmt, is_bold in inc_rows:
            c1 = ws.cell(row=r, column=1, value=label)
            c1.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold)
            c1.border = cls._border_all()
            for idx, val in enumerate(series, start=1):
                c = ws.cell(row=r, column=idx + 1, value=float(val))
                c.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold)
                c.alignment = Alignment(horizontal="right")
                c.number_format = fmt
                c.border = cls._border_all()
            r += 1

        # Spacer
        r += 1

        # Section B: Cash Flow Statement
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=n_periods + 1)
        c = ws.cell(row=r, column=1, value="CASH FLOW STATEMENT LINE ITEMS")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        cash = st.cash
        cash_rows = [
            ("Operating Cash Flow (CFO)", cash[CashStatementCols.CASH_OPERATING], "$#,##0", True),
            ("Capital Expenditures (CapEx)", cash[CashStatementCols.CAPEX], "$#,##0", False),
            ("Depreciation & Amortization (D&A)", cash[CashStatementCols.DEPRECIATION], "$#,##0", False),
        ]

        for label, series, fmt, is_bold in cash_rows:
            c1 = ws.cell(row=r, column=1, value=label)
            c1.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold)
            c1.border = cls._border_all()
            for idx, val in enumerate(series, start=1):
                c = ws.cell(row=r, column=idx + 1, value=float(val))
                c.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold)
                c.alignment = Alignment(horizontal="right")
                c.number_format = fmt
                c.border = cls._border_all()
            r += 1

        # Spacer
        r += 1

        # Section C: Balance Sheet
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=n_periods + 1)
        c = ws.cell(row=r, column=1, value="BALANCE SHEET LINE ITEMS")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        bal = st.balance
        bal_rows = [
            ("Cash & Cash Equivalents", bal[BalanceSheetCols.CASH_ON_HAND], "$#,##0", True),
            ("Total Current Assets", bal[BalanceSheetCols.TOTAL_CURRENT_ASSETS], "$#,##0", False),
            ("Total Current Liabilities", bal[BalanceSheetCols.TOTAL_CURRENT_LIABILITIES], "$#,##0", False),
            ("Total Debt Outstanding", bal[BalanceSheetCols.TOTAL_DEBT], "$#,##0", True),
            ("Total Stockholders' Equity", bal[BalanceSheetCols.TOTAL_EQUITY], "$#,##0", True),
        ]

        for label, series, fmt, is_bold in bal_rows:
            c1 = ws.cell(row=r, column=1, value=label)
            c1.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold)
            c1.border = cls._border_all()
            for idx, val in enumerate(series, start=1):
                c = ws.cell(row=r, column=idx + 1, value=float(val))
                c.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_bold)
                c.alignment = Alignment(horizontal="right")
                c.number_format = fmt
                c.border = cls._border_all()
            r += 1

        cls._auto_fit_columns(ws, min_width=16)

    # -------------------------------------------------------------------------
    # Sheet 3: WACC & Macro Framework
    # -------------------------------------------------------------------------
    @classmethod
    def _build_wacc_sheet(
        cls,
        ws,
        resp: CalculateDCFResponse,
        req: CalculateDCFRequest | None
    ) -> None:
        subtitle = f"Company: {resp.ticker}   |   Cost of Capital (WACC), CAPM & Capital Structure Architecture"
        cls._style_header_banner(ws, "WEIGHTED AVERAGE COST OF CAPITAL (WACC) SPECIFICATION", subtitle, max_col=4)

        r = 4

        # Section 1: Cost of Equity
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        c = ws.cell(row=r, column=1, value="1. COST OF EQUITY (CAPM)")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        equity_items = [
            ("Risk-Free Benchmark Yield (Rf, 10Y Sovereign)", resp.risk_free_rate, "0.00%"),
            ("Levered Systematic Risk Parameter (Beta)", resp.beta, "0.00"),
            ("Equity Risk Premium (Damodaran Country ERP)", resp.equity_risk_premium, "0.00%"),
            ("Calculated Cost of Equity [Re = Rf + Beta x ERP]", resp.cost_of_equity, "0.00%"),
        ]

        for label, val, fmt in equity_items:
            is_calc = "Calculated Cost" in label
            c1 = ws.cell(row=r, column=1, value=label)
            c2 = ws.cell(row=r, column=2, value=val)
            c1.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_calc)
            c2.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_calc)
            c1.border = cls._border_all()
            c2.border = cls._border_all()
            c2.alignment = Alignment(horizontal="right")
            c2.number_format = fmt
            if is_calc:
                c1.fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
                c2.fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
            r += 1

        r += 1

        # Section 2: Cost of Debt
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        c = ws.cell(row=r, column=1, value="2. COST OF DEBT")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        tax = resp.tax_rate
        post_tax_rd = resp.cost_of_debt
        pre_tax_rd = post_tax_rd / (1 - tax) if (1 - tax) > 0 else post_tax_rd

        debt_items = [
            ("Total Debt Principal", resp.total_debt, "$#,##0"),
            ("Effective Corporate Tax Rate (t)", tax, "0.0%"),
            ("Pre-Tax Cost of Debt (Rd)", pre_tax_rd, "0.00%"),
            ("After-Tax Cost of Debt [Rd x (1 - t)]", post_tax_rd, "0.00%"),
        ]

        for label, val, fmt in debt_items:
            is_calc = "After-Tax Cost" in label
            c1 = ws.cell(row=r, column=1, value=label)
            c2 = ws.cell(row=r, column=2, value=val)
            c1.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_calc)
            c2.font = Font(name=cls.FONT_FAMILY, size=10, bold=is_calc)
            c1.border = cls._border_all()
            c2.border = cls._border_all()
            c2.alignment = Alignment(horizontal="right")
            c2.number_format = fmt
            if is_calc:
                c1.fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
                c2.fill = PatternFill(start_color=cls.PAPER, end_color=cls.PAPER, fill_type="solid")
            r += 1

        r += 1

        # Section 3: Capital Structure & WACC
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        c = ws.cell(row=r, column=1, value="3. CAPITAL STRUCTURE & COMPOSITE WACC")
        c.font = Font(name=cls.FONT_FAMILY, size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=cls.NAVY_MED, end_color=cls.NAVY_MED, fill_type="solid")
        ws.row_dimensions[r].height = 24
        r += 1

        # Denominator total capital
        total_equity_val = resp.equity_value if resp.equity_value > 0 else (resp.current_price * resp.shares_outstanding)
        total_cap = total_equity_val + resp.total_debt
        we = total_equity_val / total_cap if total_cap > 0 else 1.0
        wd = resp.total_debt / total_cap if total_cap > 0 else 0.0

        wacc_items = [
            ("Market Equity Value (E)", total_equity_val, "$#,##0"),
            ("Total Debt Outstanding (D)", resp.total_debt, "$#,##0"),
            ("Total Capital Employed (E + D)", total_cap, "$#,##0"),
            ("Weight of Equity [We = E / (E + D)]", we, "0.0%"),
            ("Weight of Debt [Wd = D / (E + D)]", wd, "0.0%"),
            ("Weighted Average Cost of Capital (WACC)", resp.wacc, "0.00%"),
        ]

        for label, val, fmt in wacc_items:
            is_final = "Weighted Average Cost" in label
            c1 = ws.cell(row=r, column=1, value=label)
            c2 = ws.cell(row=r, column=2, value=val)
            c1.font = Font(name=cls.FONT_FAMILY, size=11 if is_final else 10, bold=is_final, color=cls.NAVY_DARK)
            c2.font = Font(name=cls.FONT_FAMILY, size=11 if is_final else 10, bold=is_final, color=cls.NAVY_DARK)
            c1.border = cls._border_all()
            c2.border = cls._border_all()
            c2.alignment = Alignment(horizontal="right")
            c2.number_format = fmt
            if is_final:
                c1.fill = PatternFill(start_color=cls.BRASS_LIGHT, end_color=cls.BRASS_LIGHT, fill_type="solid")
                c2.fill = PatternFill(start_color=cls.BRASS_LIGHT, end_color=cls.BRASS_LIGHT, fill_type="solid")
            r += 1

        cls._auto_fit_columns(ws, min_width=18)
