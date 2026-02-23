from dataclasses import dataclass
from typing import Optional, List

from my_project.infrastructure.HTTP.http_requests import HTTPFetch, HTTPFetchConfig
from my_project.infrastructure.HTTP.process_http import ProcessHTTPRequests


@dataclass
class FinnhubConfig:
    API_key: str

class FinnhubData(HTTPFetch):
    def __init__(self, config: FinnhubConfig, search_config: HTTPFetchConfig):
        super().__init__(search_config)
        self.__api_key = config.API_key

    def get_peers(self, ticker: str, industry_type: Optional[str] = None) -> List[str]:
        """

        """

        if industry_type:
            assert industry_type in ['sector', 'industry', 'subIndustry'], \
                f"[ERROR] Invalid industry type: {industry_type}"
        else:
            industry_type = 'industry'

        url = "https://finnhub.io/api/v1/stock/peers"
        params = {
            'symbol': ticker.upper(),
            'grouping': industry_type,
            'token': self.__api_key
        }

        res = self.search(url, params=params)

        res = ProcessHTTPRequests.parse_json(res)

        return list(res)

