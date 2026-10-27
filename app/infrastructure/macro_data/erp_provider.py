'''
app/infrastructure/macro_data/data/erp_provider.py
'''
import difflib
from pathlib import Path
import pandas as pd

class DamodaranERPProvider:

    _ALIASES = {
        "usa": "united states",
        "us": "united states",
        "uk": "united kingdom",
        "south korea": "korea",
    }


    def __init__(self, csv_path: Path | str | None = None,  cutoff: float = 0.75): #Is this the right way to handle this?
        _path = Path(csv_path) if csv_path else Path(__file__).resolve().parent / "data" / "damodaran_erp_2025.csv"
        _data = pd.read_csv(_path, index_col = 'Country')

        self._cutoff = cutoff
        self._map = {country.strip().lower() : float(value) for country, value in _data['Final ERP'].to_dict().items()}

    def get_equity_premium(self, country: str) -> float:
        ''''''

        matched_country = self._resolve_country(country = country)
        if matched_country is None:
            raise KeyError(f"Could not find Equity Premium for {country}")
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