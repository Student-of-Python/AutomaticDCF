""""
Responsiblity: Fundamentals macro trend data accordingly
Assuming from MACROTRENDS.COM

"""""
from my_project.infrastructure.Fundamentals.request_fundamentals import StatementType
from my_project.infrastructure.HTTP.process_http import ProcessHTTPRequests
from dataclasses import dataclass
from requests import Response
import pandas as pd
from typing import Optional


@dataclass
class ProcessMacroFundamentalsConfigs:
    years_back: int = 3

    def __post_init__(self):
        self.years_back = max(0, self.years_back)


class ProcessMacroFundamentals:
    def __init__(self, period: int):
        self.period = max(0, period)

    @staticmethod
    def _align_columns(data: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        """
        :param data:
        :param mapping:
        :return:
        """
        try:
            new_dataframe = data[[old_columns for old_columns in mapping.values()]]
        except ValueError as error:
            raise ValueError(f"Column is missing or not found | {error}")
        new_dataframe.columns = [new_column for new_column in mapping.keys()]
        return new_dataframe

    #TODO: Make a seperate calculation class? This doesn't look good :(
    @staticmethod
    def _calc_net_debt(data: pd.DataFrame) -> Optional[pd.DataFrame]:
        assert "totalDebt" in data.columns, f"[ERROR] totalDebt not in data: {data.columns}"
        assert "cashOnHand" in data.columns, f"[ERROR] cashOnHand not in data: {data.columns}"

        data['netDebt'] = data['totalDebt'] - data['cashOnHand']
        data = data.drop(columns=['cashOnHand'])

        return data

    @staticmethod
    def _calc_net_working_capital(data: pd.DataFrame) -> Optional[pd.DataFrame]:
        assert "totalCurrentAssets" in data.columns, f"[ERROR] totalCurrentAssets not in data: {data.columns}"
        assert "totalCurrentLiabilities" in data.columns, f"[ERROR] totalCurrentLiabilities not in data: {data.columns}"

        data['netWorkingCapital'] = data['totalCurrentAssets'] - data['totalCurrentLiabilities']
        data = data.drop(columns=['totalCurrentAssets', 'totalCurrentLiabilities'])

        return data

    @staticmethod
    def _calc_free_cash_flow(data: pd.DataFrame) -> Optional[pd.DataFrame]:
        assert "cashOperating" in data.columns, f"[ERROR] cashOperating not in data: {data.columns}"
        assert "capEx" in data.columns, f"[ERROR] capEx not in data: {data.columns}"

        data['freeCashFlow'] = data['cashOperating'] - data['capEx']
        data = data.drop(columns=['cashOperating'])

        return data

    def process_data(self, data: Response, statement_type: StatementType) -> Optional[pd.DataFrame]:
        """
        :param data:
        :param statement_type:
        :return:
        """

        if statement_type == StatementType.income_statement:
            data =  self._process_income_stmt(data)[:self.period]

        elif statement_type == StatementType.balance_statement:
            data =  self._process_balance_stmt(data)[:self.period]

        elif statement_type == StatementType.cash_statement:
            data =  self._process_cash_stmt(data)[:self.period]

        data *= 1_000_000 #Reported in Millions (ASSUMED)

        return data

    def _process_income_stmt(self, data: Response) -> Optional[pd.DataFrame]:
        """
        :param data:
        :return:
        """
        table = ProcessHTTPRequests.parse_dataframe_from_response(data)

        table = self._align_columns(table, StatementType.income_statement.columns)

        return table

    def _process_balance_stmt(self, data: Response) -> Optional[pd.DataFrame]:
        """

        :param data:
        :return:
        """
        table = ProcessHTTPRequests.parse_dataframe_from_response(data)

        table = self._align_columns(table, StatementType.balance_statement.columns)

        #Net Debt

        table = self._calc_net_debt(table)

        #Net Working Capital

        table = self._calc_net_working_capital(table)

        return table

    def _process_cash_stmt(self, data: Response) -> Optional[pd.DataFrame]:
        """
        :param data:
        :return:
        """

        table = ProcessHTTPRequests.parse_dataframe_from_response(data)

        table = self._align_columns(table, StatementType.cash_statement.columns)

        #Free Cash Flow

        table = self._calc_free_cash_flow(table)

        return table
