'''
app/external/api/request.py
'''
from pydantic import BaseModel, Field
from app.domain.services.forecasting.interface import ForecastStrategy
from app.domain.services.forecasting.strategies import (
    HistoricalAverageForecast,
    RollingAverageForecast,
    LinearConvergenceForecast,
)


class StrategyRequest(BaseModel):
    strategy: str = Field("historical", description="Strategy type: historical | rolling | linear")
    window: int | None = Field(None, ge=1, description="Window size in years (for rolling or historical window)")
    target_rate: float | None = Field(None, description="Target rate for linear convergence (e.g. 0.025 for 2.5%, 0.20 for 20% margin)")


class ValuationRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (ex: AAPL)")
    horizon: int = Field(5, ge=1, le=20, description="Forecast horizon in years")
    growth: float = Field(0.025,description="Terminal growth rate of the company")
    exit_multiple: float | None = Field(None,  description="Exit multiple [OVERRIDE]")
    risk_free: float | None = Field(None, description='Risk free rate [OVERRIDE]')
    erp: float | None = Field(None, description='Equity Risk Premium [OVERRIDE]')
    revenue_strat: StrategyRequest | None = None
    ebit_strat: StrategyRequest | None = None
    capex_strat: StrategyRequest | None = None
    da_strat: StrategyRequest | None = None
    nwc_strat: StrategyRequest | None = None


def create_driver_strategy(
        spec: StrategyRequest | None = None,
        default_target: float | None = None) -> ForecastStrategy:
    '''Instaniates a strategy'''
    if spec is None or spec.strategy == 'historical':
        window = spec.window if spec else None
        return HistoricalAverageForecast(window = window)

    elif spec.strategy == 'rolling':
        window = spec.window or 3 #3 is the default for now
        return RollingAverageForecast(window = window)

    elif spec.strategy == 'linear':
        target = spec.target_rate if spec.target_rate is not None else default_target
        if target is None:
            raise ValueError("Target rate required for linear convergence strategy")
        return LinearConvergenceForecast(terminal_rate = target)

    else:
        raise ValueError(f"Unknown Strategy recieved: {spec.strategy}. Avaliable strategies are 'historical' , 'rolling', 'linear' .")