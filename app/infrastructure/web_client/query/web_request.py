'''
app/infrastructure/web_client/query/web_request.py
'''
from app.domain import Result, Error, ErrorCode
from typing import TypeVar, Optional
import requests
import time


class WebRequest:
    '''
    Returns HTML of the website.

    1. Needs to handle errors
    '''

    def __init__(self):
        self._wait = 60 #60 seconds too much?
        self._timeout = 60

        self._header = {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/141.0.0.0 Safari/537.36"
                        )
                        }


    def request(self, url: str, params: Optional[dict] = None) -> Result:
        '''

        Requests contents from the url. Returns the contents

        :args:
            url: string formatted url to request
            params: optional parameters to pass into request

        '''

        _attempted = False #This will not make any sense. Does not reset locally.

        res = requests.get(url = url, params=params, headers=self._header, timeout = self._timeout,  allow_redirects=True)

        try:
           res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if res.status_code == 429 and not _attempted:
                #Too many requests in short amount of time.
                print(f"Too many requests in short amount of time: {err}")
                print(f"Waiting: {self._wait} seconds")
                time.sleep(self._wait)
                _attempted = True
                return self.request(url = url, params = params)

            return Result.failed(
                error = Error.failed_request(
                    request_msg = res.reason,
                    params = {
                        'reason' : res.json(),
                        'url' : url,
                        'params' : params
                    }
                )
            )

        return Result.success(result = res)


