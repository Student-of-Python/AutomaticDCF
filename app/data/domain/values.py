'''
app/data/domain/values.py

holds dataclasses
'''
from dataclasses import dataclass
from pandas import DataFrame
from typing import Optional



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
    host_country: str
    beta: float
    shares_outstanding: float
    ev_multiple: Optional[float]
