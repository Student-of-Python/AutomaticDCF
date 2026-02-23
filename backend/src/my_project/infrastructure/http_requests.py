""""
Search.py
=========
Responsibility
Given URL, it will scrape content and return it
"""""
from dataclasses import dataclass
from requests import Response
from typing import Optional
import requests

@dataclass
class HTTPFetchConfig:
    max_size_mb: int = 1
    timeout: int = 10
    headers: Optional[dict] = None

class HTTPFetch:
    def __init__(self, config: HTTPFetchConfig):
        self._config = config

        if self._config.headers is None:
            self._config.headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/141.0.0.0 Safari/537.36"
                )}
        self._session = requests.Session()


    def search(self, url: str, params: Optional[dict] = None) -> Optional[Response]:
        """
        :param url: Any URL
        :param params: params
        :return: http response
        """

        if not self._is_safe(url):
            return None

        res = self._session.get(
            url=url,
            params=params,
            timeout=self._config.timeout,
            headers=self._config.headers,
        )
        res.raise_for_status()
        return res



    def _is_safe(self, url: str,) -> bool:
        """
        :param url: Any URL
        :return: if URL is safe (size overload)
        """

        head = self._session.head(
            url=url,
            timeout=self._config.timeout,
            headers=self._config.headers,
            allow_redirects=True
        )

        size = int(head.headers.get('Content-Length', 0))
        max_length = self._config.max_size_mb * 1024 ** 2

        if size > max_length:
            return False
            #raise MemoryError(f"[ERROR] URL content size ({size}) exceeds {max_length}: {url}")
        return True






