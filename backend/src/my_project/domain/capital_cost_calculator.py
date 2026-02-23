from dataclasses import dataclass
from typing import Union, Optional


@dataclass
class CapitalCostConfig:
    beta: Union[float, int]
    risk_free: Union[float, int] #Risk Free Rate
    equity_risk_prem: Union[float, int] #Equity Premuim Rate
    tax_rate: Union[float,int]

    #Cost of Debt:
    interest_expense: Union[float, int]
    total_debt: Union[float, int]

    #Cost of Equity:
    total_equity: Union[float, int]




class CapitalCostCalculator:
    """
    Responsibility: Calculate CAPM (WACC)

    Cost of Equity
    Cost of Debt
    """
    def __init__(self, config: CapitalCostConfig):
        self._config = config

    def get_cost_of_debt(self) -> Union[float, int]:
        return self._config.interest_expense / self._config.total_debt

    def get_cost_of_equity(self) -> Union[float, int]:
        return self._config.risk_free + self._config.beta + self._config.equity_risk_prem

    def get_wacc(self) -> Union[float, int]:
        """
        Computes the Weighted Average Cost of Capital (WACC).

        Formula:
            WACC = (Ce * (E / (E + D))) + (Cd * (D / (E + D)) * (1 - T))

        where:
            Ce = Cost of equity
            Cd = Cost of debt
            E = Total equity
            D = Total debt
            T = Tax rate

        Returns:
            float: Weighted average cost of capital (decimal form).
        """

        Ce = self.get_cost_of_equity()
        Cd = self.get_cost_of_debt()

        E = self._config.total_equity
        D = self._config.total_debt

        T = self._config.tax_rate

        return (Ce * (E / (E + D))) + (Cd * (D / (E + D)) * (1 - T))


