'''
app/infrastructure/api/yfinance_profile.py
'''
from app.interface.profile_interface import ProfileAdapter
from typing import Any
import yfinance as yf


class YFinanceProfileAdapter(ProfileAdapter):

    _FIELD_MAPPING = {'country' : 'country',
                'beta' : 'beta',
                'shares_outstanding' : 'sharesOutstanding',
                'current_price' : 'previousClose',
                'ev_ebitda_multiple' : 'enterpriseToEbitda'}


    def __init__(self, ticker: str):
        self._ticker = ticker


    def _fetch_profile_data(self) -> dict[str, Any]:
        '''Gets necessary info'''

        info = yf.Ticker(ticker = self._ticker).info

        return self._convert(info)

    @staticmethod
    def _convert(data: dict[str, Any]) -> dict[str, Any]:
        '''Converts yfinance names to internal'''

        return {k : data.get(v) for k,v in YFinanceProfileAdapter._FIELD_MAPPING.items()}

