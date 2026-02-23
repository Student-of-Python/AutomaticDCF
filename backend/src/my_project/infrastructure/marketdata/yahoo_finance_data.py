from dataclasses import dataclass
import yfinance as yf

@dataclass
class YahooFinanceProfileConfig:
    ticker: str


class YahooFinanceData:
    @staticmethod
    def get_profile(ticker: str):
        try:
            return yf.Ticker(ticker.upper()).info
        except Exception as error:
            raise Exception(f"[ERROR] Could not request data from yfinance: {error}")

