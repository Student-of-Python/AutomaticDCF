'''
app/application/dto.py
'''
from __future__ import annotations
from typing import TYPE_CHECKING
from app.domain.services.forecasting.interface import ProjectedCashFlowSchedule
from dataclasses import dataclass

if TYPE_CHECKING:
    from app.domain.entities import FinancialStatements

@dataclass(frozen = True)
class CalculateDCFRequest:
    '''Inputs needed to calculate DCF'''
    ticker: str
    horizon: int = 3
    terminal_growth_rate: float = 0.025
    exit_multiple: float | int | None = None
    risk_free_rate: float| None = None
    equity_risk_premium: float | None = None

    def __post_init__(self):
        #Input Validation
        object.__setattr__(self, 'ticker', self._clean_ticker())

        if not self.ticker:
            raise ValueError(f"Invalid Ticker recieved: {self.ticker}. Cannot have spacing, or no valid at all.")

        if self.horizon <= 0:
            raise ValueError("Horizon must be a positive integer")

        if self.exit_multiple is not None and self.exit_multiple <= 0:
            raise ValueError(f"Exit Multiple must be positive number")

        if self.risk_free_rate is not None and self.risk_free_rate <= 0:
            raise ValueError(f"Risk Free Rate must be positive; Negative yields not supported")

        if self.equity_risk_premium is not None and self.equity_risk_premium <= 0:
            raise ValueError(f"Equity Risk Premium must be positive")

    def _clean_ticker(self) -> str:
        ''''''
        return self.ticker.strip().upper()


@dataclass(frozen = True)
class CalculateDCFResponse:
    ticker: str
    current_price: float
    implied_share_price: float
    wacc: float
    enterprise_value: float
    equity_value: float
    pv_fcff: float
    pv_terminal_value: float
    schedule: ProjectedCashFlowSchedule
    shares_outstanding: int = 0
    cash: float = 0.0
    total_debt: float = 0.0
    cost_of_equity: float = 0.0
    cost_of_debt: float = 0.0
    tax_rate: float = 0.0
    risk_free_rate: float = 0.0
    equity_risk_premium: float = 0.0
    beta: float = 1.0
    terminal_growth_rate: float = 0.025
    exit_multiple: float | None = None
    historical_statements: FinancialStatements | None = None

    @property
    def upside_downside_pct(self) -> float:
        '''Percent change from current price'''
        return (self.implied_share_price / self.current_price) - 1 if self.current_price > 0 else 0.0
