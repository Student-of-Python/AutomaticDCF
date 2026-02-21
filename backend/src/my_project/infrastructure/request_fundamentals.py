""""
Request Fundamentals
======================
Responsibility: Request and extract fundemental data
"""

from my_project.config import RequestFundamentalsConfig
import requests

class RequestFundamentals:
    def __init__(self, config: RequestFundamentalsConfig):
        self._ticker = config.ticker
        self._url = f"https://www.macrotrends.net/stocks/charts/{self._ticker}"

    @property
    def url(self) -> str:
        return self._url

    def request(self) -> None:
        requests.request()


