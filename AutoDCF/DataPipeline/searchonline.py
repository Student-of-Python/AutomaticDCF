from typing import Callable, Optional, List, Union, Any
from bs4 import BeautifulSoup
import pandas as pd
import os
import dotenv
import requests
import re
import time


# Load environment variables (Google API + CX keys)
env = dotenv.load_dotenv()
cx_key = os.getenv('cx_key', None)
google_search_key = os.getenv('google_search_key', None)
assert cx_key, f'[ERROR] Missing cx_key'
assert google_search_key, f'[ERROR] Missing google search key'

# Default HTTP headers for web requests
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/141.0.0.0 Safari/537.36"
    )
}


def getLinkContentTable(url: str):
    """
    Decorator that automatically fetches HTML table data from a given URL
    and injects it into the wrapped function.

    Args:
        url (str): The URL to extract HTML table data from.

    Returns:
        Callable: Decorated function with an added 'table' argument
                  containing the parsed HTML table(s) as a DataFrame.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            url_list = [url]
            table = get_link_contents(url_list, output='table')
            return func(table=table, *args, **kwargs)

        return wrapper

    return decorator


def get_google_links(search_phrase: str, amount: Optional[int] = 5) -> Optional[List[str]]:
    """
    Executes a Google Custom Search query and retrieves a list of result links.

    Args:
        search_phrase (str): Search phrase for the query.
        amount (Optional[int]): Number of links to fetch (default = 5, capped at 10).

    Returns:
        list[str]: A list of result URLs.

    Raises:
        ValueError: If no search results are found for the given query.
        requests.exceptions.RequestException: If the request fails.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': search_phrase,
        'key': google_search_key,
        'cx': cx_key,
        'num': max(amount, 10),
    }

    res = requests.get(url, params=params, timeout=5)
    res.raise_for_status()
    data = res.json()

    if 'items' not in data:
        raise ValueError(f"[ERROR] No items found for search phrase '{search_phrase}'")

    links = [item['link'] for item in data['items'] if 'items' in data]
    if not links:
        raise ValueError(
            f'''[ERROR] No available links (size : {len(links)}) for search phrase "{search_phrase}" '''
        )

    return links


def isLinkSafe(url: str, max_size_mb: Optional[int] = 1) -> bool:
    """
    Validates whether a URL can be safely accessed and downloaded.

    Performs a HEAD request to verify accessibility and content size.

    Args:
        url (str): Target URL to check.
        max_size_mb (Optional[int]): Maximum allowed file size in MB (default = 1).

    Returns:
        bool: True if the URL is accessible and under size limits, else False.
    """
    try:
        head = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        head.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f'[SKIP] Cannot access {url} due to {error}')
        return False

    content_size = int(head.headers.get('Content-Length', 0))
    if content_size > max_size_mb * 1024 ** 2:
        print(f'[SKIP] File too large ({(content_size / 1024**2):.2f} MB) at {url}')
        return False

    return True


def get_link_contents(links: List[str], output: str) -> Optional[List]:
    """
    Fetches and parses web page contents from a list of URLs.

    Args:
        links (list[str]): List of URLs to request and parse.
        output (str): Output format, either:
            - 'table': Extract HTML tables as DataFrames.
            - 'raw_contents': Return raw HTML bytes.

    Returns:
        list or object: Parsed contents from all URLs.
                        Returns a single element if only one result is available.

    Raises:
        AssertionError: If output argument is invalid.
    """
    assert output.lower() in ['table', 'raw_contents']
    contents = []

    for url in links:
        if isLinkSafe(url):
            time.sleep(3)
            try:
                res = requests.get(url, headers=headers, timeout=5)
                res.raise_for_status()
            except requests.exceptions.RequestException as error:
                print(f'[SKIP] Cannot access {url} due to {error}')
                continue

            data = res.content
            if output.lower() == 'table':
                try:
                    table = pd.read_html(data)
                    contents.extend(table)
                except Exception as error:
                    print(f'[ERROR] Could not extract data from {url} into table format: {error}')
                    continue
            else:
                contents.append(data)

    return contents[0] if len(contents) == 1 else contents


def choose_from_contents(
    contents: List[str],
    *,
    keyword: str,
    keyword_regex: str,
    choose: bool = False,
    func: Optional[Callable[[Any], Any]] = None,
) -> Union[str, float, int, None]:
    """
    Filters and extracts keyword-related results from web content.

    Optionally applies a transformation function and allows manual user selection.

    Args:
        contents (list[str]): List of raw HTML strings or text snippets.
        keyword (str): Keyword to locate in the content.
        keyword_regex (str): Regex pattern to extract numeric or textual data.
        choose (bool): If True, interactively prompts the user for selection.
        func (Callable, optional): Optional transformation function to apply to results.

    Returns:
        Union[str, float, int, None]: First or user-selected match.

    Raises:
        AssertionError: If func is provided but not callable.
    """
    if func:
        assert callable(func), '[ERROR] func must be a callable'

    phrases = sum(
        [find_phrase(content=content, keyword=keyword, keyword_regex=keyword_regex)
         for content in contents],
        []
    )
    results = sum(
        [re.findall(rf'{keyword_regex}', phrase, re.IGNORECASE) for phrase in phrases],
        []
    )

    if func:
        results = [func(elem) for elem in results]

    if not choose:
        return results[0]

    # Interactive selection from console
    for result, phrase in zip(results, phrases):
        if str(input(f'[CHOOSE] Press Y to accept following {keyword} in phrase: '
                     f'\n \t{phrase}\n Detected {keyword}: {result}\n')).lower() == 'y':
            return result

    # Manual user input fallback
    while True:
        user_input = input(
            f'[CHOOSE] Exhausted search results.\n'
            f'If CAGR, input as percentage (%), otherwise as decimal.\n'
            f'Please input a suitable {keyword}: '
        )
        if func:
            try:
                user_input = func(user_input)
            except ValueError:
                print(f'[ERROR] Unable to convert {user_input} using {func}. Try again.\n')
                continue
        return user_input


def find_phrase(keyword: str, content: str, keyword_regex: str) -> Optional[List[str]]:
    """
    Extracts text snippets surrounding a specific keyword and regex pattern.

    Args:
        keyword (str): Keyword to search for within the HTML content.
        content (str): Raw HTML content string.
        keyword_regex (str): Regex pattern to extract numeric or textual data.

    Returns:
        list[str] or None: List of matching text fragments containing keyword and pattern.
    """
    soup = BeautifulSoup(content, 'html.parser')

    # Remove non-textual elements
    for element in soup(['script', 'style', 'meta', 'noscript', 'iframe']):
        element.decompose()

    text = soup.get_text(separator=' ', strip=True)

    possible_phrase = re.findall(
        rf'[^.?!]*\b{re.escape(keyword)}\b[^.?!]*{keyword_regex}',
        text,
        flags=re.IGNORECASE
    )
    return possible_phrase if possible_phrase else []


def search(
    search_phrase: str,
    keyword: str,
    keyword_regex: str,
    amount: Optional[int] = 5,
    output: Optional[str] = 'raw_contents',
    choose: Optional[bool] = False,
    func: Optional[Callable[[Any], Any]] = None,
) -> Union[str, int, float]:
    """
    Executes a full Google Search → Parse → Extract workflow.

    High-level pipeline:
        1. Searches Google for the given phrase.
        2. Fetches content from the top results.
        3. Extracts data matching the keyword and regex pattern.
        4. Optionally applies a converter or allows manual selection.

    Args:
        search_phrase (str): Search query.
        keyword (str): Keyword to locate in the content.
        keyword_regex (str): Regex pattern for extracting data.
        amount (Optional[int]): Number of search results to consider (default = 5).
        output (Optional[str]): Output mode ('table' or 'raw_contents').
        choose (Optional[bool]): Enable manual selection if multiple matches.
        func (Callable, optional): Function to convert result (e.g., percent → float).

    Returns:
        Union[str, int, float]: Extracted result (converted if applicable).
    """
    links = get_google_links(search_phrase, amount)
    contents = get_link_contents(links, output)
    result = choose_from_contents(
        contents,
        keyword=keyword,
        keyword_regex=keyword_regex,
        choose=choose,
        func=func
    )
    return result
