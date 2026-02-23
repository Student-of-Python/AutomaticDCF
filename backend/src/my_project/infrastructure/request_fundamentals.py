""""
Request Fundamentals
======================
Responsibility: Return Fundemental Data for ticker from MACROTRENDS
"""
from http_requests import HTTPFetch, HTTPFetchConfig
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import pandas as pd
import requests

@dataclass
class RequestFundamentalsConfig:
    ticker: str
    years: int = 3
    pass

class StatementType(Enum):
    """
    Statement Types Required:
    Income Statement
    Cash Statement
    Balance Statement
    """
    income_statement = (
        {
        'revenue': 'Revenue',
        'ebitda': 'EBITDA',
        'ebt': 'Pre-Tax Income',
        'incomeTaxExpense': 'Income Taxes',
        'interestExpense': 'Total Non-Operating Income/Expense'
        },
        "income-statement")

    cash_statement = (
        {
        'DA': 'Total Depreciation And Amortization - Cash Flow',
        'capEx': 'Net Change In Property, Plant, And Equipment',
        'cashOperating': 'Cash Flow From Operating Activities'
        },
        "cash-flow-statement")

    balance_statement = (
        {
        'totalEquity': 'Share Holder Equity',
        'totalDebt': 'Long Term Debt',
        'totalCurrentAssets': 'Total Current Assets',
        'totalCurrentLiabilities': 'Total Current Liabilities',
        'cashOnHand': 'Cash On Hand'
        },
        'balance-sheet')

    def __init__(self, columns: dict, macro_label: str):
        self.columns = columns
        self.macro_label = macro_label


class RequestMacroFundamentals(HTTPFetch):

    @staticmethod
    #TODO: A way to make this cleaner (or remove?)
    def _get_complete_url(ticker: str, statement_type: StatementType) -> str:
        """
        :param ticker: Ticker in macrotrends
        :return: Complete URL
        For some reason, MACROTRENDS url can be funky. Not optimal solution
        """
        incomplete_url = f"https://www.macrotrends.net/stocks/charts/{ticker}"
        response = requests.get(incomplete_url, allow_redirects=True,
                                headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        return f"{response.url}{statement_type.macro_label}"

    def __init___(self, config: RequestFundamentalsConfig, search_config: HTTPFetchConfig):
        """
        :param config: Config Attributes
        :param request: http request obj
        :return:
        """
        super().__init__(search_config)
        self._config = config

    def request_macro_data(self, statement_type: StatementType):
        """
        :param statement_type:
        :return:
        """

        url = self._get_complete_url(self._config.ticker, statement_type)

        return self.search(url)


    def _get_url(self, statement_type: StatementType) -> str:
        return self._get_complete_url(self._config.ticker, statement_type)





