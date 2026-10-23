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
            revenue_growth= rev.pct_change().dropna().to_numpy(),
            ebit_margin = (statements.income[IncomeStatementCols.EBIT] / rev).to_numpy(),
            capex_ratio = (statements.cash[CashStatementCols.CAPEX].abs() / rev).to_numpy(),
            da_ratio = (statements.cash[CashStatementCols.DEPRECIATION] / rev).to_numpy(),
            nwc_ratio = ((statements.balance[BalanceSheetCols.TOTAL_CURRENT_ASSETS] - statements.balance[BalanceSheetCols.TOTAL_CURRENT_LIABILITIES]) / rev).to_numpy(),
            latest_revenue = statements.latest_revenue,
            latest_nwc = statements.latest_nwc
        )