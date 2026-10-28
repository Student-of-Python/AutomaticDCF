"""
test/unit/test_excel_export.py

Unit tests verifying the multi-sheet Excel valuation report generator.
"""
import io
import openpyxl
import pandas as pd
import pytest
from app.application.dto import CalculateDCFResponse, CalculateDCFRequest
from app.domain.entities import FinancialStatements
from app.domain.enums import IncomeStatementCols, CashStatementCols, BalanceSheetCols
from app.domain.services.forecasting.interface import ProjectedCashFlowSchedule
from app.external.export.excel_generator import ExcelReportGenerator


@pytest.fixture
def mock_dcf_response() -> CalculateDCFResponse:
    # Minimal mock dataframes for financial statements
    dates = pd.date_range("2023-12-31", periods=3, freq="-1YE")
    income_df = pd.DataFrame({
        IncomeStatementCols.REVENUE: [1000.0, 900.0, 800.0],
        IncomeStatementCols.EBITDA: [300.0, 270.0, 240.0],
        IncomeStatementCols.EBIT: [250.0, 220.0, 190.0],
        IncomeStatementCols.PRETAX_INCOME: [240.0, 210.0, 180.0],
        IncomeStatementCols.INCOME_TAX_EXPENSE: [50.0, 44.0, 38.0],
        IncomeStatementCols.INTEREST_EXPENSE: [10.0, 10.0, 10.0],
    }, index=dates)

    cash_df = pd.DataFrame({
        CashStatementCols.CASH_OPERATING: [220.0, 190.0, 160.0],
        CashStatementCols.CAPEX: [40.0, 35.0, 30.0],
        CashStatementCols.DEPRECIATION: [50.0, 50.0, 50.0],
    }, index=dates)

    balance_df = pd.DataFrame({
        BalanceSheetCols.CASH_ON_HAND: [150.0, 130.0, 110.0],
        BalanceSheetCols.TOTAL_CURRENT_ASSETS: [400.0, 350.0, 300.0],
        BalanceSheetCols.TOTAL_CURRENT_LIABILITIES: [200.0, 180.0, 160.0],
        BalanceSheetCols.TOTAL_DEBT: [100.0, 100.0, 100.0],
        BalanceSheetCols.TOTAL_EQUITY: [500.0, 450.0, 400.0],
    }, index=dates)

    sched = ProjectedCashFlowSchedule(
        revenues=[1100.0, 1210.0, 1331.0],
        ebits=[275.0, 302.5, 332.75],
        capex=[45.0, 50.0, 55.0],
        nopats=[217.25, 238.97, 262.87],
        da=[55.0, 60.0, 65.0],
        nwc=[220.0, 242.0, 266.2],
        delta_nwc=[20.0, 22.0, 24.2],
        fcff=[207.25, 226.97, 248.67]
    )

    return CalculateDCFResponse(
        ticker="TEST",
        current_price=150.0,
        implied_share_price=180.0,
        wacc=0.085,
        enterprise_value=2500.0,
        equity_value=2550.0,
        pv_fcff=550.0,
        pv_terminal_value=1950.0,
        schedule=sched,
        shares_outstanding=14,
        cash=150.0,
        total_debt=100.0,
        cost_of_equity=0.095,
        cost_of_debt=0.045,
        tax_rate=0.21,
        risk_free_rate=0.042,
        equity_risk_premium=0.05,
        beta=1.06,
        terminal_growth_rate=0.025,
        exit_multiple=None,
        historical_statements=FinancialStatements(
            income=income_df,
            balance=balance_df,
            cash=cash_df
        )
    )


def test_excel_generator_structure(mock_dcf_response: CalculateDCFResponse):
    xlsx_bytes = ExcelReportGenerator.generate(mock_dcf_response)
    assert isinstance(xlsx_bytes, bytes)
    assert len(xlsx_bytes) > 2000

    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
    expected_sheets = ["DCF Valuation Model", "Historical Financials", "WACC & Assumptions"]
    assert wb.sheetnames == expected_sheets

    # Verify Sheet 1
    ws1 = wb["DCF Valuation Model"]
    assert ws1.views.sheetView[0].showGridLines is True
    assert "DISCOUNTED CASH FLOW" in str(ws1["A1"].value)
    assert ws1["B11"].value == 2550.0  # Implied Equity Value
    assert ws1["B13"].value == 180.0   # Implied DCF Fair Value per Share

    # Verify Sheet 2
    ws2 = wb["Historical Financials"]
    assert ws2.views.sheetView[0].showGridLines is True
    assert "HISTORICAL FINANCIAL STATEMENTS" in str(ws2["A1"].value)

    # Verify Sheet 3
    ws3 = wb["WACC & Assumptions"]
    assert ws3.views.sheetView[0].showGridLines is True
    assert "WEIGHTED AVERAGE COST OF CAPITAL" in str(ws3["A1"].value)


def test_api_excel_export_endpoint():
    from fastapi.testclient import TestClient
    from app.external.api.main import app

    client = TestClient(app)
    # Invalid ticker test
    err_res = client.post("/api/v1/export/excel", json={"ticker": "", "horizon": 3})
    assert err_res.status_code == 400
