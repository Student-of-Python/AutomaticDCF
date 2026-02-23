from typing import Optional, Union
import pandas as pd
from my_project.infrastructure.HTTP.http_requests import HTTPFetch, HTTPFetchConfig
from my_project.infrastructure.HTTP.process_http import ProcessHTTPRequests


class YieldRateSearch(HTTPFetch):
    def __init__(self, search_config: HTTPFetchConfig):
        super().__init__(search_config)

    def _get_table(self, country_name: str) -> Optional[pd.DataFrame]:
        """
        :param country_name:
        :return: Risk Free Rate
        """

        url = "https://tradingeconomics.com/bonds"

        res = self.search(url)

        tables = ProcessHTTPRequests.parse_table(res) #Bunch of tables in list format, need to concat


        columns = ['index', 'Country', 'Yield', 'Day', 'Weekly', 'Monthly', 'YTD', 'YoY', 'Date']

        table = pd.concat([df.rename(columns={old : new for old,new in zip(df.columns, columns)}) for df in tables])

        return table



    def get_yield_rate(self, country_name: str) -> Optional[float]:
        table = self._get_table(country_name)

        yield_rate = table.query("Country == @country_name")['Yield'].iat[0]

        if not yield_rate:
            raise ValueError(f"[ERROR] Could not get yield rate for: {country_name}")

        yield_rate = float(yield_rate)

        return float(yield_rate / 100)


