'''
app/domain/services/wacc.py
'''
from dataclasses import dataclass

@dataclass(frozen=True)
class WaccCalculator:
    risk_free_rate: float
    equity_premium: float
    beta: float
    total_debt: float | int
    total_equity: float | int
    interest_expense: float
    tax_rate: float

    @property
    def cost_of_equity(self) -> float:
        ''''''
        return self.risk_free_rate + self.beta * self.equity_premium

    @property
    def cost_of_debt(self) -> float:
        ''''''
        return self.interest_expense / self.total_debt if self.total_debt > 0 else 0.0

    @property
    def post_tax_cost_of_debt(self) -> float:
        ''''''
        return self.cost_of_debt * (1 - self.tax_rate)

    @property
    def equity_weight(self) -> float:
        ''''''
        return self.total_equity / self._denominator

    @property
    def debt_weight(self) -> float:
        ''''''
        return self.total_debt / self._denominator

    @property
    def wacc(self) -> float:
        '''Returns Wacc'''
        return (self.equity_weight * self.cost_of_equity) + (self.debt_weight * self.post_tax_cost_of_debt)

    @property
    def _denominator(self) -> float:
        ''''''
        _total_capital = self.total_debt + self.total_equity
        if _total_capital <= 0.0:
            raise ValueError(f"Total Capital (debt + equity) can never less or equal to 0 when calculating wacc: {_total_capital}")
        return _total_capital