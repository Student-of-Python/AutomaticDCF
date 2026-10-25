'''
app/infrastructure/api/default_macro.py
'''
from app.interface.variables_interface import MacroAdapter, RiskFree, EquityPremium


class DefaultMacroAdapter(MacroAdapter):

    def _fetch_data(self, country: str) -> tuple[RiskFree, EquityPremium]:
        '''
            Default, dummy values
        '''
        return 0.045 , 0.05
