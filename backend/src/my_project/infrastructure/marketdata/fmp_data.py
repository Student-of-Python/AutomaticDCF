

from my_project.infrastructure.HTTP.http_requests import HTTPFetch, HTTPFetchConfig
from my_project.infrastructure.HTTP.process_http import ProcessHTTPRequests
from dataclasses import dataclass
import pandas as pd
from typing import Optional


@dataclass
class FMPDataConfig:
    ticker: str
    API_key: str

class FMPData(HTTPFetch):
    def __init__(self, ticker: str, config: FMPDataConfig, search_config: HTTPFetchConfig):
        super().__init__(search_config)
        self.ticker = ticker
        self.__api_key = config.API_key

    def get_profile(self) -> Optional[dict]:
        """
        :param ticker:
        :return:
        """

        url = "https://financialmodelingprep.com/stable/profile"

        params = {
            "symbol": self.ticker,
            "apikey": self.__api_key,
        }

        res = self.search(url, params)

        res = ProcessHTTPRequests.parse_json(res)

        return res





