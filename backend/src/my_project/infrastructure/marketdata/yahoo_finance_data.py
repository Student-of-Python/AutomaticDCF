import yfinance as yf

class YahooFinanceData:
    @staticmethod
    def get_profile(ticker: str):
        try:
            return yf.Ticker(ticker.upper()).info
        except Exception as error:
            raise Exception(f"[ERROR] Could not request data from yfinance: {error}")

    def __init__(self, ticker: str):
        self.ticker = ticker

        self._profile = self.get_profile(ticker)


    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value



