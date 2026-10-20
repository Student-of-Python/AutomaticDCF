'''
app/data/domain/entities.py

holds dataclasses
'''
from __future__ import annotations
from .enums import ErrorCode
from dataclasses import dataclass
from pandas import DataFrame
from typing import Optional, Any



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
    country: str
    beta: float
    shares_outstanding: int
    current_price: float
    ev_ebitda_multiple: float | int | None = None

@dataclass(frozen=True)
class CompanyProfile:
    '''
    Company Profile
    '''
    host_country: str
    beta: float
    shares_outstanding: float
    ev_multiple: Optional[float]

@dataclass(frozen=True)
class MacroVariables:
    '''
    Macro Economic Variables
    '''

    yield_rate: float
    equity_premium: float

@dataclass(frozen=True)
class Error:
    code: ErrorCode
    msg: str
    details: Optional[dict[str, Any]] = None

    @classmethod
    def failed_request(cls, request_msg: str, params: dict) -> Error:
        return cls(code = ErrorCode.FAILED_REQUEST, msg = request_msg, details = params)

    @classmethod
    def invalid_data(cls, msg: str, details: dict) -> Error:
        return cls(code = ErrorCode.INVALID_DATA, msg = msg, details = details)

    def __repr__(self) -> str:
        return (f'ERROR: {self.code} '
                f'MSG: {self.msg} '
                f'DETAILS: {self.details}')

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

class InvalidDataTypeError(Exception):
    pass
