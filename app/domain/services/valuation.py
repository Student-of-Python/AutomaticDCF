'''
app/domain/services/valuation.py
'''
from dataclasses import dataclass

@dataclass(frozen=True)
class ValuationCalculator:
    fcffs: list[float]
    terminal_ebitda: float
    wacc: float
    cash: float
    total_debt: float | int
    shares_outstanding: int | float
    terminal_growth_rate: float
    exit_multiple: float | None =  None

    def __post_init__(self):
        if self.shares_outstanding <= 0:
            raise ValueError("Shares Outstanding must be positive")
        if len(self.fcffs) <= 0:
            raise ValueError("Future cash flows must have at least 1 future cash flow, got none")
        if self.wacc <= 0:
            raise ValueError("WACC must be positive number")


    @property
    def pv_fcff(self) -> float:
        '''Returns present value of the future cash flows'''
        return sum(fcff / ((1 + self.wacc) ** t) for t, fcff in enumerate(self.fcffs, start=1))



    def terminal_value_perpetuity(self) -> float:
        '''Terminal value by perpetuity'''
        if self.wacc <= self.terminal_growth_rate:
            raise ValueError(f"Perpetuity method does not allow WACC <= Terminal Growth Rate")

        return (self.fcffs[-1] * (1 + self.terminal_growth_rate)) / (self.wacc - self.terminal_growth_rate)

    def terminal_value_exit_multiple(self) -> float:
        '''Terminal value by exit multiple'''
        if self.exit_multiple is None:
            raise ValueError(f"Exit Multiple cannot be None for exit multiple method!")

        return self.terminal_ebitda * self.exit_multiple

    @property
    def terminal_value(self) -> float:
        '''Returns undiscounted year N terminal value.'''

        if self.exit_multiple is not None:
            return self.terminal_value_exit_multiple()
        return self.terminal_value_perpetuity()

    @property
    def pv_terminal_value(self) -> float:
        '''Returns discounted terminal value'''
        return self.terminal_value / ((1 + self.wacc) ** len(self.fcffs))

    @property
    def enterprise_value(self) -> float:
        '''returns enterprice value: PV (FCFF) + PV(TV)'''
        return self.pv_fcff + self.pv_terminal_value

    @property
    def equity_value(self) -> float:
        '''Returns equity value: EV + Cash - Total Debt'''
        return self.enterprise_value + self.cash - self.total_debt

    @property
    def implied_share_price(self) -> float:
        '''Returns implied share price. Returns 0.0 if negative price (cannot have negative share price'''
        return max(0.0, self.equity_value / self.shares_outstanding)