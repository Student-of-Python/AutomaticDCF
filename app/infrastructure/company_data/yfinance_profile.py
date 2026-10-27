'''
app/infrastructure/company_data/yfinance_profile.py
'''
from app.application.ports import ProfileAdapter
from typing import Any
import yfinance as yf


class YFinanceProfileAdapter(ProfileAdapter):

    _FIELD_MAPPING = {'country' : 'country',
                'beta' : 'beta',
                'shares_outstanding' : 'sharesOutstanding',
                'current_price' : 'previousClose',
                'ev_ebitda_multiple' : 'enterpriseToEbitda'}


    def _fetch_profile_data(self, ticker: str) -> dict[str, Any]:
        '''Gets necessary info'''

        info = yf.Ticker(ticker = ticker).info

        return self._convert(info)

    @staticmethod
    def _convert(data: dict[str, Any]) -> dict[str, Any]:
        '''Converts yfinance names to internal'''

        return {k : data.get(v) for k,v in YFinanceProfileAdapter._FIELD_MAPPING.items()}

