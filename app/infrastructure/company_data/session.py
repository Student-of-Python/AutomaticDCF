"""
app/infrastructure/company_data/session.py

Shared session factory for Yahoo Finance API queries.
Impersonates authentic browser TLS fingerprints (JA3/JA4) using curl_cffi.
Loads proxy configurations securely from the root .env file via python-dotenv.
"""
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# Explicitly resolve root .env (3 levels up: app/infrastructure/company_data -> project root)
ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()  # Fallback to current working directory search



def get_yfinance_session() -> Any:
    """
    Returns a browser-impersonating HTTP session for yfinance with optional proxy routing.
    Reads proxy URL securely from the .env environment variable `YFINANCE_PROXY`.
    """
    proxy_url = os.environ.get("YFINANCE_PROXY", "").strip()

    try:
        from curl_cffi import requests as cffi_requests
        session = cffi_requests.Session(impersonate="chrome")
        if proxy_url:
            session.proxies = {"http": proxy_url, "https": proxy_url}
        return session
    except ImportError:
        import requests
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        if proxy_url:
            session.proxies = {"http": proxy_url, "https": proxy_url}
        return session
