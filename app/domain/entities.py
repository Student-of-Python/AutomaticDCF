'''
app/data/domain/entities.py

holds dataclasses
'''
from __future__ import annotations
from dataclasses import dataclass
from pandas import DataFrame
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


