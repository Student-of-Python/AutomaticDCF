'''
app\infrastructure\api\yfinance_data.py
'''
from app.domain.enums import IncomeStatementCols, CashStatementCols, BalanceSheetCols
from app.application.ports.statements_interface import StatementAdapter, Income, Balance, Cash
import yfinance as yf




class YFinanceStatementsAdapter(StatementAdapter):
    '''
    Notes: Yahoofinance limited to only 4 years historical -- not bad for MVP, but may need to extend later on.
    #TODO: Update the mappings based on the new statements cols added.
    #TODO: Add years back later? For now, sticking to 4 years.
    '''

    def _fetch_raw_statements(self, ticker: str) -> tuple[Income, Balance, Cash]:
        ''''''
        _ticker = yf.Ticker(ticker = ticker)

        income = _ticker.income_stmt.T
        balance = _ticker.balance_sheet.T
        cash = _ticker.cash_flow.T

        common = (
            income.index
            .intersection(balance.index)
            .intersection(cash.index)
        )

        if common.empty:
            raise ValueError(f"No overlapping financial statement dates found for '{ticker}'.")

        return income.loc[common], balance.loc[common], cash.loc[common]

    @property
    def _income_mapping(self) -> dict[str, str]:
        return {
        'Total Revenue': IncomeStatementCols.REVENUE,
        'EBITDA': IncomeStatementCols.EBITDA,
        'EBIT': IncomeStatementCols.EBIT,
        'Pretax Income' : IncomeStatementCols.PRETAX_INCOME,
        'Tax Provision' : IncomeStatementCols.INCOME_TAX_EXPENSE,
        'Interest Expense' : IncomeStatementCols.INTEREST_EXPENSE
    }

    @property
    def _balance_mapping(self) -> dict[str, str]:
        return {
        'Stockholders Equity': BalanceSheetCols.TOTAL_EQUITY,
        'Total Debt': BalanceSheetCols.TOTAL_DEBT,
        'Current Assets': BalanceSheetCols.TOTAL_CURRENT_ASSETS,
        'Current Liabilities': BalanceSheetCols.TOTAL_CURRENT_LIABILITIES,
        'Cash And Cash Equivalents': BalanceSheetCols.CASH_ON_HAND,
    }

    @property
    def _cash_mapping(self) -> dict[str, str]:
        return {
        'Depreciation And Amortization': CashStatementCols.DEPRECIATION,
        'Capital Expenditure': CashStatementCols.CAPEX,
        'Operating Cash Flow': CashStatementCols.CASH_OPERATING,
    }
