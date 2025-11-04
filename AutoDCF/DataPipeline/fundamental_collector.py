"""
Extract Fundamental Data
========================
Primary Data Source: Macrotrends (via web scraping)

This module provides helper functions and a class to retrieve and process
fundamental financial data (Income Statement, Balance Sheet, and Cash Flow)
for a given company ticker symbol using Macrotrends.net.

Includes utilities to align, clean, and enrich data (e.g., compute Free Cash Flow,
Net Debt, and Net Working Capital).
"""

from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import re
import json


def get_net_debt(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Net Debt as `totalDebt - cashOnHand`.

    Args:
        data (pd.DataFrame): Balance sheet DataFrame with 'totalDebt' and 'cashOnHand' columns.

    Returns:
        pd.DataFrame: Updated DataFrame with a 'netDebt' column added.

    Raises:
        KeyError: If the required columns are missing.
    """
    try:
        data['netDebt'] = data['totalDebt'] - data['cashOnHand']
        data = data.drop(columns=['cashOnHand'])
    except KeyError as error:
        print(f"Error calculating netDebt: {error}")
        raise KeyError
    return data


def align_data_columns(data: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Aligns and renames columns of a DataFrame based on a provided mapping dictionary.

    Args:
        data (pd.DataFrame): Input DataFrame to align.
        mapping (dict): Mapping dictionary where `{new_name: old_name}`.

    Returns:
        pd.DataFrame: DataFrame with renamed and aligned columns.

    Raises:
        ValueError: If one or more expected columns are missing.
    """
    try:
        new_dataframe = data[[old_columns for old_columns in mapping.values()]]
    except ValueError as error:
        raise ValueError(f"Column is missing or not found | {error}")
    new_dataframe.columns = [new_column for new_column in mapping.keys()]
    return new_dataframe


def get_free_cash_flow(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Free Cash Flow as `cashOperating - capEx`.

    Args:
        data (pd.DataFrame): Cash flow DataFrame containing 'cashOperating' and 'capEx' columns.

    Returns:
        pd.DataFrame: DataFrame with 'freeCashFlow' column added.

    Raises:
        KeyError: If required columns are missing.
    """
    try:
        data['freeCashFlow'] = data['cashOperating'] - data['capEx']
        data = data.drop(columns=['cashOperating'])
    except KeyError as error:
        print(f"Error calculating freeCashFlow: {error}")
        raise KeyError
    return data


def get_net_working_capital(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Net Working Capital as `totalCurrentAssets - totalCurrentLiabilities`.

    Args:
        data (pd.DataFrame): Balance sheet DataFrame with relevant columns.

    Returns:
        pd.DataFrame: DataFrame with 'netWorkingCapital' column added.

    Raises:
        KeyError: If required columns are missing.
    """
    try:
        data['netWorkingCapital'] = data['totalCurrentAssets'] - data['totalCurrentLiabilities']
        data = data.drop(columns=['totalCurrentAssets', 'totalCurrentLiabilities'])
    except KeyError as error:
        print(f"Error calculating NetWorkingCapital: {error}")
        raise KeyError
    return data


def has_missing_values(data: pd.DataFrame) -> bool:
    """
    Checks whether a DataFrame contains any missing (NaN) values.

    Args:
        data (pd.DataFrame): Input DataFrame.

    Returns:
        bool: True if missing values exist, False otherwise.
    """
    return data.isnull().values.any()



class ExtractFundamentals:
    """
    A scraper and processor for company financial data from Macrotrends.net.

    Attributes:
        ticker (str): Stock ticker symbol.
        years_back (int): Number of historical years to include.
        complete_url (str): The resolved Macrotrends URL for the ticker.
    """

    @staticmethod
    def _json_from_html(contents: str) -> json:
        """
        Extracts the embedded JSON ("originalData") object from Macrotrends HTML.

        Args:
            contents (str): HTML source of a Macrotrends financial statement page.

        Returns:
            json: Parsed JSON array containing financial data.

        Raises:
            ValueError: If 'originalData' is not found in the HTML.
        """
        soup = BeautifulSoup(contents, 'html.parser')
        script_tags = soup.find_all('script')

        for script in script_tags:
            if script.string and 'originalData' in script.string:
                match = re.search(r"var originalData = (\[.*?\]);", script.string, re.DOTALL)
                if match:
                    return json.loads(match.group(1))

        raise ValueError("Could not find originalData JSON in page")

    @staticmethod
    def _json_to_dataframe(json_data: json) -> pd.DataFrame:
        """
        Converts extracted JSON data into a cleaned and transposed DataFrame.

        Args:
            json_data (json): Raw JSON data parsed from Macrotrends.

        Returns:
            pd.DataFrame: Structured financial data with numeric columns.
        """
        records = []
        for entry in json_data:
            raw_field = entry.get('field_name', '')
            clean_field = BeautifulSoup(raw_field, "html.parser").get_text(strip=True)

            row = {k: v for k, v in entry.items() if k not in ["field_name", "popup_icon"]}
            row["field_name"] = clean_field
            records.append(row)

        df = pd.DataFrame(records).set_index("field_name").T
        df = df.apply(pd.to_numeric, errors="coerce")
        df.dropna(how='all', axis=1, inplace=True)
        return df

    income_mapping = {
        'revenue': 'Revenue',
        'ebitda': 'EBITDA',
        'ebt': 'Pre-Tax Income',
        'incomeTaxExpense': 'Income Taxes',
        'interestExpense': 'Total Non-Operating Income/Expense'  # Closest available
    }

    cash_mapping = {
        'DA': 'Total Depreciation And Amortization - Cash Flow',
        'capEx': 'Net Change In Property, Plant, And Equipment',
        'cashOperating': 'Cash Flow From Operating Activities'
    }

    balance_mapping = {
        'totalEquity': 'Share Holder Equity',
        'totalDebt': 'Long Term Debt',
        'totalCurrentAssets': 'Total Current Assets',
        'totalCurrentLiabilities': 'Total Current Liabilities',
        'cashOnHand': 'Cash On Hand'
    }

    statements_mapping = {
        'income': ('income-statement', income_mapping),
        'cash': ('cash-flow-statement', cash_mapping),
        'balance': ('balance-sheet', balance_mapping)
    }


    def __init__(self, ticker: str, years_back: int = 4):
        """
        Initializes the extractor and resolves the base URL for the given ticker.

        Args:
            ticker (str): Company ticker symbol (e.g., 'AAPL', 'NVDA').
            years_back (int, optional): Number of historical years to fetch. Defaults to 4.
        """
        self.ticker = str(ticker)
        self.years_back = int(years_back)

        incomplete_url = f"https://www.macrotrends.net/stocks/charts/{self.ticker}"
        response = requests.get(incomplete_url, allow_redirects=True,
                                headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        self.complete_url = response.url


    def get_macrotrend_data(self, statement_type: str) -> pd.DataFrame:
        """
        Retrieves, parses, and processes a financial statement (Income, Cash Flow, or Balance Sheet)
        for the initialized ticker.

        Automatically performs column mapping, trimming, and derived metric calculations
        (e.g., Free Cash Flow, Net Debt, and Net Working Capital).

        Args:
            statement_type (str): One of {'income', 'cash', 'balance'}.

        Returns:
            pd.DataFrame: Processed financial statement data, scaled to actual values (not millions).

        Raises:
            ValueError: If the statement type is invalid or data cannot be parsed.
        """
        # Unpack mapping for the statement type
        statement_tuple = self.statements_mapping.get(statement_type)
        if not statement_tuple:
            raise ValueError(f"Invalid statement type: {statement_type}")

        macro_statement, mapping = statement_tuple

        # Fetch statement HTML
        time.sleep(5)  # Prevent rapid request blocks
        complete_url = f"{self.complete_url}{macro_statement}"
        response = requests.get(complete_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        response.raise_for_status()

        # Parse and transform JSON -> DataFrame
        json_data = self._json_from_html(response.text)
        df = self._json_to_dataframe(json_data)
        df = df[:self.years_back]
        df = align_data_columns(df, mapping)

        # Apply derived metric functions
        if macro_statement == 'cash-flow-statement':
            df = get_free_cash_flow(df)
        if macro_statement == 'balance-sheet':
            df = get_net_debt(df)
            df = get_net_working_capital(df)

        # Convert from millions to actual units
        df *= 1_000_000
        return df
