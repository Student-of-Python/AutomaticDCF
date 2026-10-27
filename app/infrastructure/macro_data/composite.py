'''
app/infrastructure/macro_data/composite.py
'''
from app.application.ports.variables_interface import MacroAdapter, EquityPremiumProvider, RiskFreeProvider, RiskFree, \
    EquityPremium

from .erp_provider import DamodaranERPProvider
from .yield_provider import TradingEconomicsYieldProvider

class CompositeMacroAdapter(MacroAdapter):
    def __init__(self, yield_provider: RiskFreeProvider, equity_provider: EquityPremiumProvider):
        self._yield_provider = yield_provider or TradingEconomicsYieldProvider()
        self._equity_provider = equity_provider or DamodaranERPProvider()


    def _fetch_data(self, country: str) -> tuple[RiskFree, EquityPremium]:
        '''Fetchs Risk Free and Equity Premium data'''

        risk_free = self._yield_provider.get_risk_free(country = country)

        equity_premium = self._equity_provider.get_equity_premium(country = country)

        return risk_free, equity_premium


