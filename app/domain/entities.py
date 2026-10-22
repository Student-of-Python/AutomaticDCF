'''
app/data/domain/entities.py

holds dataclasses
'''
from __future__ import annotations
from dataclasses import dataclass
from pandas import DataFrame
from .enums import IncomeStatementCols, CashStatementCols, BalanceSheetCols
from .exceptions import Error

@dataclass(frozen=True)
class FinancialStatements:
    '''
    3 Financial Statements

    --> Should these be dataframes, or some other data type?
    '''
    income: DataFrame
    balance: DataFrame
    cash: DataFrame

    @property
    def latest_total_debt(self) -> float:
        '''Returns most recent total debt. Assumes ordering is recent to oldest.'''
        return self.balance[BalanceSheetCols.TOTAL_DEBT].iat[0]

    @property
    def latest_interest_expense(self) -> float:
        '''Returns most recent interest_expense. Assumes ordering is recent to oldest.'''
        return self.income[IncomeStatementCols.INTEREST_EXPENSE].iat[0]

    @property
    def latest_cash_and_equivalents(self) -> float:
        return self.balance[BalanceSheetCols.CASH_ON_HAND].iat[0]

    @property
    def latest_ebitda(self) -> float:
        return self.income[IncomeStatementCols.EBITDA].iat[0]

    def effective_tax_rate(self, default_rate: float = 0.21) -> float:
        '''returns effective rate rate, if not <= 0'''

        #TODO: Default rate depends on country, we need to consider this down the line.

        if (pretax_income := self.income[IncomeStatementCols.PRETAX_INCOME].iat[0]) <= 0:
            return default_rate

        raw_rate = self.income[IncomeStatementCols.INCOME_TAX_EXPENSE].iat[0] / pretax_income

        tax_rate = raw_rate if 0 <= raw_rate <= 0.5 else default_rate #Creates upper and lower bound

        return tax_rate

@dataclass(frozen=True)
class CompanyProfile:
    '''
    Company Profile
    '''
    country: str
    beta: float
    shares_outstanding: int
    current_price: float
    ev_ebitda_multiple: float | int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, str | float | int | None]) -> CompanyProfile:
        '''Converts to dictionary'''
        return CompanyProfile(
            country = data['country'],
            beta = data['beta'],
            shares_outstanding = data['shares_outstanding'],
            current_price = data['current_price'],
            ev_ebitda_multiple = data['ev_ebitda_multiple'],
        )

@dataclass(frozen=True)
class MacroVariables:
    '''
    Macro Economic Variables
    '''

    yield_rate: float
    equity_premium: float


@dataclass(frozen=True)
class Result[T]:
    value: T | None = None
    error: Error | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None

    @classmethod
    def success(cls, result: T) -> Result[T]:
        return cls(value=result)

    @classmethod
    def failed(cls, error: Error) -> Result[T]:
        return cls(error = error)


