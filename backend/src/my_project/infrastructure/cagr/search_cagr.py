""""
Responsibility: Get a bunch of links that have CAGR data

"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from my_project.infrastructure.HTTP.http_requests import HTTPFetch, HTTPFetchConfig

from my_project.infrastructure.HTTP.process_http import ProcessHTTPRequests


@dataclass
class RequestCagrConfig:
    entries: int
    ticker: str
    industry: str

    #API
    key: str
    cx_key: str


class RequestCagr(HTTPFetch):
    def __init__(self, config: RequestCagrConfig, search_config: HTTPFetchConfig):
        super().__init__(search_config)
        self._settings = config

    def _search_cagr_links(self) -> Optional[List[str]]:
        """
        :return: List of potential google links that contain Cagr
        """

        url = "https://www.googleapis.com/customsearch/v1"

        #TODO: Find a more suitable search phrase
        search_phrase = f"{self._settings.ticker} {self._settings.industry} CAGR GROWTH"


        params = {
            'q' : search_phrase,
            'key' : self._settings.key,
            'cx_key' : self._settings.cx_key,
            'num' : max(10,self._settings.entries)
        }

        res = self.search(url, params)

        data = ProcessHTTPRequests.parse_json(res)

        if 'items' not in data:
            raise ValueError(f"[ERROR] No items found for search phrase '{search_phrase}'")

        links = [item['link'] for item in data['items'] if 'items' in data]

        return links

    def get_cagr_content(self) -> Optional[List[str]]:
        """
        :return: Returns contents from links
        """

        links = self._search_cagr_links()

        contents = []

        for url in links:
            res = self.search(url)

            data = ProcessHTTPRequests.parse_content(res)

            contents.append(data)

        return contents






