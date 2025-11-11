from typing import Union, Iterable, Any
from DataPipeline.searchonline import getLinkContentTable
from difflib import SequenceMatcher
import pandas as pd


def get_keyword(data: Iterable[Any], keyword: str) -> Union[None, str, int]:
    """
    Finds the element in a list or iterable most similar to a given keyword.

    Uses `difflib.SequenceMatcher` to compute similarity ratios and returns
    the closest match based on the highest ratio.

    Args:
        data (Iterable[Any]): A list, pandas columns, or other iterable of strings/names.
        keyword (str): The target keyword to compare against.

    Returns:
        Union[str, int, None]: The element in `data` that best matches `keyword`.
    """
    ratios = [SequenceMatcher(None, keyword, some_data).ratio() for some_data in data]
    index = ratios.index(max(ratios))
    return data[index]


def convert_percent_to_float(string: str) -> float:
    """
    Converts a percentage string (e.g. '4.5%') to a float (e.g. 0.045).

    Args:
        string (str): A string containing a numeric percentage.

    Returns:
        float: The numeric equivalent in decimal form.
    """
    return float(string[:-1]) / 100


def get_latest(dataframe: pd.DataFrame, column_name: str) -> Union[str, int, float, None]:
    """
    Extracts the most recent (top-row) value from a pandas DataFrame column.

    Args:
        dataframe (pd.DataFrame): DataFrame containing time-series or sequential data.
        column_name (str): Name of the column to extract the value from.

    Returns:
        Union[str, int, float, None]: The top (latest) cell value from the given column.
    """
    return dataframe[column_name].iloc[0].item()


@getLinkContentTable('https://www.iban.com/country-codes')
def get_country_from_alpha(country_alpha: str, table: None) -> Union[str, None]:
    """
    Retrieves a full country name from its ISO alpha-2 or alpha-3 country code.

    Automatically decorates the function to inject the country-code reference table
    from https://www.iban.com/country-codes.

    Args:
        country_alpha (str): The ISO country code (e.g., 'US', 'DE', 'GB').
        table (pd.DataFrame): (Injected) Table of country codes and names.

    Returns:
        Union[str, None]: Full country name corresponding to the provided code.
    """
    assert isinstance(table, pd.DataFrame), f'[ERROR] Table is not type DataFrame: {type(table)}'
    alpha_numeric_dict = dict(zip(table.iloc[:, 1], table.iloc[:, 0]))
    country_name = get_keyword([str(k) for k in alpha_numeric_dict], country_alpha)
    return alpha_numeric_dict.get(country_name, None)


@getLinkContentTable('https://tradingeconomics.com/bonds')
def get_yield_rate(country_name: str, table: None) -> Union[float, None]:
    """
    Fetches the latest sovereign bond yield for a given country.

    Decorated with a TradingEconomics table scraper that automatically retrieves
    global bond yield data.

    Args:
        country_name (str): The country name to find the yield for.
        table (list[pd.DataFrame]): (Injected) List of parsed tables containing bond yields.

    Returns:
        Union[float, None]: Yield value (as a float percentage).
    """
    assert isinstance(table, list), f'[ERROR] Table is not type list: {type(table)}'

    # Combine multiple HTML tables into one DataFrame
    dfs = [df.set_axis(range(df.shape[1]), axis=1) for df in table]
    combined_df = pd.concat(dfs, ignore_index=True)

    # Find the best match for the country name
    local_country_name = get_keyword(combined_df.iloc[:, 1].to_list(), country_name)
    combined_df = combined_df.set_index(1)

    # Extract the yield rate
    yield_value = combined_df.loc[local_country_name, 2]
    if isinstance(yield_value, pd.Series):
        yield_value = yield_value.drop_duplicates()

    return float(yield_value)


def manual_override(param_name: str):
    """
    Decorator factory for overriding automated computation with manual inputs.

    If the specified parameter name exists in `self.manual_input` and is not
    marked as "auto", the manual value is returned instead of executing the method.

    Args:
        param_name (str): The key to check in `self.manual_input`.

    Returns:
        Callable: Decorator that conditionally overrides the method.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            manual_val = self.manual_input.get(param_name)
            return manual_val if manual_val not in (None, "auto", "Auto", "AUTO") else func(self, *args, **kwargs)
        return wrapper
    return decorator


def manual_init(func):
    """
    Decorator for class initializers to sanitize manual input dictionaries.

    Filters out keys with 'auto' or None values from the provided manual inputs
    before passing them into the class constructor.

    Args:
        func (Callable): The class initializer (__init__) being decorated.

    Returns:
        Callable: Wrapped initializer with cleaned manual input dictionary.
    """
    def wrapper(self, *args, **kwargs):
        manual_dict = kwargs.get('manual_input', {})

        manual_dict = {
            key: value
            for key, value in manual_dict.items()
            if value not in (None, 'Auto', 'AUTO', 'auto')
        }
        kwargs['manual_input'] = manual_dict
        return func(self, *args, **kwargs)
    return wrapper
