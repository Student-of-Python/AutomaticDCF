from enum import StrEnum

class ErrorCode(StrEnum):
    FAILED_REQUEST = "FAILED_REQUEST"
    INVALID_DATA = 'INVALID_DATA'

class StatementCols(StrEnum):
    @classmethod
    def values_as_tuple(cls) -> tuple[str, ...]:
        return tuple(c.value for c in cls)

class IncomeStatementCols(StatementCols):
    REVENUE = 'REVENUE'
    EBITDA = 'EBITDA'
    EBIT = 'EBIT'
    #Need interest expense???



class CashStatementCols(StatementCols):
    DEPRECIATION = 'DEPRECIATION'
    CAPEX = 'CAPEX'
    CASH_OPERATING = 'CASH_OPERATING'

class BalanceSheetCols(StatementCols):
    TOTAL_EQUITY = 'TOTAL_EQUITY'
    TOTAL_DEBT = 'TOTAL_DEBT'
    TOTAL_CURRENT_ASSETS = 'TOTAL_CURRENT_ASSETS'
    TOTAL_CURRENT_LIABILITIES = 'TOTAL_CURRENT_LIABILITIES'
    CASH_ON_HAND = 'CASH_ON_HAND'