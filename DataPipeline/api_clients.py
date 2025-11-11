"""
API Clients for Financial Data
==============================

This module provides lightweight client functions for fetching
company and market data from public APIs including:

- Financial Modeling Prep (FMP)
- Yahoo Finance (via yfinance)
- Finnhub API

Environment variables for API keys are loaded automatically via `.env`.
"""

from typing import Union, List, Optional
import pandas as pd
import yfinance as yf
import requests
import dotenv
import os

dotenv.load_dotenv()
FMP_KEY = os.getenv('fmp_key', None)
FINNHUB_KEY = os.getenv('finnhub_key',None)

assert FMP_KEY, f'[ERROR] Missing FMP_KEY'
assert FINNHUB_KEY, f'[ERROR] Missing FINNHUB_KEY'


def get_fmp_profile(stock: str) -> pd.DataFrame:
    """
    Fetches company profile information from Financial Modeling Prep (FMP).

    Args:
        stock (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT').

    Returns:
        pd.DataFrame: A single-row DataFrame containing the company's profile data.

    Raises:
        Exception: If the API request fails or returns invalid data.
    """
    url = f"https://financialmodelingprep.com/api/v3/profile/{stock}"
    try:
        res = requests.get(url, params={'apikey': FMP_KEY}, timeout=5)
        res.raise_for_status()
    except Exception as error:
        raise Exception(f"[ERROR] Could not request data from FMP: {error}")

    data = res.json()
    if not data or not isinstance(data, list):
        raise ValueError(f"[ERROR] Invalid or empty response from FMP for stock '{stock}'.")

    return pd.DataFrame([data[0]])


def get_yf_info(stock: str) -> dict:
    """
    Retrieves detailed company information using Yahoo Finance via the `yfinance` library.

    Args:
        stock (str): Stock ticker symbol (e.g., 'AAPL', 'TSLA').

    Returns:
        dict: A dictionary of key-value pairs containing financial and company metadata.

    Raises:
        Exception: If the data retrieval from yfinance fails.
    """
    try:
        return yf.Ticker(stock).info
    except Exception as error:
        raise Exception(f"[ERROR] Could not request data from yfinance: {error}")


def get_finnhub_peers(stock: str, industry_type: Optional[str] = None) -> List[str]:
    """
    Retrieves a list of peer tickers (comparable companies) from the Finnhub API.

    Args:
        stock (str): The stock ticker symbol.
        industry_type (Optional[str], optional):
            The level of grouping to use for peers.
            Must be one of {'sector', 'industry', 'subIndustry'}.
            Defaults to 'industry'.

    Returns:
        List[str]: A list of peer ticker symbols.

    Raises:
        AssertionError: If `industry_type` is invalid.
        Exception: If the API request fails.
    """
    if industry_type:
        assert industry_type in ['sector', 'industry', 'subIndustry'], \
            "[ERROR] Invalid industry type"
    else:
        industry_type = 'industry'

    url = "https://finnhub.io/api/v1/stock/peers"
    params = {
        'symbol': stock,
        'grouping': industry_type,
        'token': FINNHUB_KEY
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
    except Exception as error:
        raise Exception(f"[ERROR] Could not request data from Finnhub: {error}")

    peers = res.json()
    if not isinstance(peers, list):
        raise ValueError(f"[ERROR] Unexpected response format from Finnhub for '{stock}'.")

    return peers
