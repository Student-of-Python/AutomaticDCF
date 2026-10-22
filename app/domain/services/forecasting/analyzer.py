'''
app/domain/services/forecasting/analyzer.py
'''
from app.domain.enums import IncomeStatementCols, CashStatementCols, BalanceSheetCols
from app.domain.entities import FinancialStatements
from .interface import HistoricalDriver

class HistoricalDriverAnalyzer:

    @staticmethod
    def analyze(statements: FinancialStatements) -> HistoricalDriver:
        '''Extracts historical rates'''

        rev = statements.income[IncomeStatementCols.REVENUE]

        return HistoricalDriver(
            revenue_growth= rev.pct_change().dropna().tolist(),
            ebit_margin = (statements.income[IncomeStatementCols.EBIT] / rev).tolist(),
            capex_ratio = (statements.cash[CashStatementCols.CAPEX].abs() / rev).tolist(),
            da_ratio = (statements.cash[CashStatementCols.DEPRECIATION] / rev).tolist(),
            nwc_ratio = ((statements.balance[BalanceSheetCols.TOTAL_CURRENT_ASSETS] - statements.balance[BalanceSheetCols.TOTAL_CURRENT_LIABILITIES]) / rev).tolist(),
            latest_revenue = statements.latest_revenue,
            latest_nwc = statements.latest_nwc
        )