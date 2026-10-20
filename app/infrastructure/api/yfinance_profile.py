'''
app/infrastructure/api/yfinance_profile.py
'''
from .profile_interface import ProfileAdapter
import yfinance as yf


class YFinanceProfileAdapter(ProfileAdapter):


    def __init__(self, ticker: str):
        self._info: dict[str, str] = yf.Ticker(ticker = ticker).info

    def _get_country(self) -> str | None:
        '''Gets Country'''
        return self._info.get('country', None)

    def _get_beta(self) -> float | None:
        '''returns beta'''
        return self._info.get('beta', None)


    def _get_shares_outstanding(self) -> int | None:
        '''Gets shares'''
        return self._info.get('sharesOutstanding', None)


    def _get_current_price(self) -> float | None:
        '''Gets current price'''
        return self._info.get('previousClose', None)

    def _get_ev_ebitda_multiple(self) -> float | None:
        '''Gets multiple??'''
        return self._info.get('enterpriseToEbitda', None)