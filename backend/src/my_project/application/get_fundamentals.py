""""
get fundamentals:

Gets and returns fundamentals easily
"""
import pandas as pd
from typing import Optional, Tuple

from my_project.infrastructure.Fundamentals.request_fundamentals import RequestMacroFundamentals,RequestFundamentalsConfig
from my_project.infrastructure.Fundamentals.process_fundamentals import ProcessMacroFundamentals,ProcessMacroFundamentalsConfigs
from my_project.infrastructure.Fundamentals.process_fundamentals import StatementType
from my_project.infrastructure.HTTP.http_requests import HTTPFetchConfig


class GetFundamentals:
    """"
    
    """""

    def __init__(self, ticker: str, period: int, search_config: HTTPFetchConfig):
        self._search = RequestMacroFundamentals(ticker, search_config)
        self._process = ProcessMacroFundamentals(period)

    def request_stmts(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame],Optional[pd.DataFrame]]:
        income = self.request_income_stmt()

        balance = self.request_balance_stmt()

        cash = self.request_cash_stmt()

        return income, balance, cash


    def request_income_stmt(self) -> Optional[pd.DataFrame]:
        stmt = StatementType.income_statement

        income_search = self._search.request_macro_data(stmt)

        income = self._process.process_data(income_search, stmt)

        return income

    def request_balance_stmt(self) -> Optional[pd.DataFrame]:
        stmt = StatementType.balance_statement

        balance_search = self._search.request_macro_data(stmt)

        balance = self._process.process_data(balance_search, stmt)

        return balance

    def request_cash_stmt(self) ->Optional[pd.DataFrame]:
        stmt = StatementType.cash_statement

        cash_search = self._search.request_macro_data(stmt)

        cash = self._process.process_data(cash_search, stmt)

        return cash




