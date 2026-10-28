from enum import StrEnum

class StatementCols(StrEnum):
    @classmethod
    def values_as_tuple(cls) -> tuple[str, ...]:
        return tuple(c.value for c in cls)

class StrategyChoice(StrEnum):
    HISTORICAL_AVG = 'Historical Average'
    LINEAR_CONV = 'Linear Convergence'
    ROLLING_AVG = 'Rolling Average'

class MetricName(StrEnum):
    REV = 'Revenue Growth'
    EBIT = 'Ebit Margin'
    CAPEX = 'CapEx Ratio'
    DA = 'D&A Ratio'
    NWC = 'NWC Ratio'

class IncomeStatementCols(StatementCols):
    REVENUE = 'REVENUE'
    EBITDA = 'EBITDA'
    EBIT = 'EBIT'
    INTEREST_EXPENSE = 'INTEREST_EXPENSE'
    PRETAX_INCOME = 'PRETAX_INCOME'
    INCOME_TAX_EXPENSE = 'INCOME_TAX_EXPENSE'

class CashStatementCols(StatementCols):
    CASH_OPERATING = 'CASH_OPERATING'
    DEPRECIATION = 'DEPRECIATION'
    CAPEX = 'CAPEX'

class BalanceSheetCols(StatementCols):
    TOTAL_EQUITY = 'TOTAL_EQUITY'
    TOTAL_DEBT = 'TOTAL_DEBT'
    TOTAL_CURRENT_ASSETS = 'TOTAL_CURRENT_ASSETS'
    TOTAL_CURRENT_LIABILITIES = 'TOTAL_CURRENT_LIABILITIES'
    CASH_ON_HAND = 'CASH_ON_HAND'

