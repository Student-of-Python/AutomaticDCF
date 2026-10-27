'''
app/infrastructure/macro_data/yield_provider.py
'''
import requests
import pandas as pd
import io
import difflib

class TradingEconomicsYieldProvider:

    _ALIASES = {
        "usa": "united states",
        "us": "united states",
        "uk": "united kingdom",
        "south korea": "korea",
    }

    def __init__(self, cutoff: float = 0.75, timeout: float = 10.0):
        self._cutoff = cutoff
        self._timeout = timeout
        self._map: dict[str, float] | None = None

    def get_risk_free(self, country: str) -> float:
        ''''''
        self._get_map()
        matched_country = self._resolve_country(country = country)
        if matched_country is None:
            raise KeyError(f"Could not find Risk Free Rate for {country}")
        return self._map[matched_country]

    def _resolve_country(self, country: str) -> str | None:
        '''Finds country name, if detected'''
        normalized_country = country.strip().lower()

        if normalized_country in self._map:
            return normalized_country

        elif normalized_country in self._ALIASES:
            return self._ALIASES[normalized_country]

        elif _matches := difflib.get_close_matches(normalized_country, self._map,n=1,cutoff=self._cutoff):
            return _matches[0]

        return None


    def _get_map(self):
        if self._map is None:
            self._map = self._fetch_yield_map()



    def _fetch_yield_map(self) -> dict[str, float]:
        ''''''
        _url = "https://tradingeconomics.com/bonds"
        _HEADERS = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(_url, headers=_HEADERS, timeout = self._timeout)
        response.raise_for_status()

        tables = pd.read_html(io.StringIO(response.text))

        dfs = [
            df.iloc[:, [1, 2]].set_axis(["country", "yield"], axis=1)
            for df in tables
            if df.shape[1] >= 3
        ]

        bonds_df = (
            pd.concat(dfs, ignore_index=True)
            .assign(
                country=lambda x: x["country"].astype(str).str.strip().str.lower(),
                yield_rate=lambda x: pd.to_numeric(x["yield"] / 100, errors="coerce"),
            )
            .dropna(subset=["country", "yield_rate"])
            .drop_duplicates(subset=["country"], keep="first")
        )

        return bonds_df.set_index("country")["yield_rate"].to_dict()

