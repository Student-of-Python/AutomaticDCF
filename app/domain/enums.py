from enum import StrEnum

class ErrorCode(StrEnum):
    FAILED_REQUEST = "FAILED_REQUEST"

class IncomeStatementCols(StrEnum):
    REVENUE = 'REVENUE'
    EBITDA = 'EBITDA'
    EBIT = 'EBIT'
    #Need interest expense???

class CashStatementCols(StrEnum):
    DEPRECIATION = 'DEPRECIATION'
    CAPEX = 'CAPEX'
    CASH_OPERATING = 'CASH_OPERATING'

class BalanceSheetCols(StrEnum):
    TOTAL_EQUITY = 'TOTAL_EQUITY'
    TOTAL_DEBT = 'TOTAL_DEBT'
    TOTAL_CURRENT_ASSETS = 'TOTAL_CURRENT_ASSETS'
    TOTAL_CURRENT_LIABILITIES = 'TOTAL_CURRENT_LIABILITIES'
    CASH_ON_HAND = 'CASH_ON_HAND'