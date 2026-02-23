from country_alignment import most_similiar
from typing import Optional
import pandas as pd




class ERP:
    @staticmethod
    def get_risk_free_rate(country_name: str) -> Optional[float]:
        #Load
        excel_sheet = pd.read_excel('Data/RiskFreeRates.xlsx', sheet_name="Sheet1")

        #Align
        country_column = excel_sheet['Country'].dropna().astype(str).to_list()
        local_name = most_similiar(country_name, country_column)

        erp = excel_sheet.query("Country == @local_name")['Final ERP'].item()

        if not erp:
            raise ValueError(f"[ERROR] Could not find ERP value for {local_name}.")

        return float(erp)

