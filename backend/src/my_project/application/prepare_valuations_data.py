from dataclasses import dataclass
from typing import Union, Literal
from enum import Enum
import pandas as pd

from my_project.application.get_fundamentals import GetFundamentals
from my_project.infrastructure.Fundamentals.process_fundamentals import ProcessMacroFundamentalsConfigs
from my_project.infrastructure.Fundamentals.request_fundamentals import RequestFundamentalsConfig
from my_project.infrastructure.HTTP.http_requests import HTTPFetchConfig
from my_project.infrastructure.marketdata.finnhub_data import FinnhubConfig, FinnhubData
from my_project.infrastructure.marketdata.fmp_data import FMPDataConfig, FMPData
from my_project.infrastructure.marketdata.yahoo_finance_data import YahooFinanceData

class MethodType(Enum):
    perpetuity = None
    ev_multiple = None



@dataclass
class MasterConfig:
    income_stmt: pd.DataFrame
    balance_stmt: pd.DataFrame
    cash_stmt: pd.DataFrame

    wacc: Union[int, float]
    cagr: Union[int, float]

    #Modes
    method: MethodType

@dataclass
class InputConfig:
    #Financials:
    search_config: HTTPFetchConfig
    request_config: RequestFundamentalsConfig
    process_config: ProcessMacroFundamentalsConfigs

    #Market Data
    finnhub_config: FinnhubConfig
    fmp_config: FMPDataConfig


class CapitalCostConfig:
    beta: Union[float, int]
    risk_free: Union[float, int] #Risk Free Rate
    equity_risk_prem: Union[float, int] #Equity Premuim Rate
    tax_rate: Union[float,int]

    #Cost of Debt:
    interest_expense: Union[float, int]
    total_debt: Union[float, int]

    #Cost of Equity:
    total_equity: Union[float, int]


class ValuationAttributes:
    def __init__(self, ticker: str, period: int, inputs_configs: InputConfig):
        ticker = ticker.upper()
        period = max(2, period)
        self._financials = GetFundamentals(ticker, period, inputs_configs.search_config)

        self._finhub = FinnhubData(inputs_configs.finnhub_config, inputs_configs.search_config)
        self._fmp = FMPData(ticker, inputs_configs.fmp_config, inputs_configs.search_config)
        self._yahoo = YahooFinanceData(ticker)



    def execute(self, ):
        #stmts
        income_stmt, balance_stmt, cash_stmt = self._financials.request_stmts()

        #Capm
        beta = self._fmp.get_profile().get('beta')
        risk_free =








        return {}

