'''
app/domain/services/forecasting/interface.py
'''
from typing import Protocol, Sequence
from dataclasses import dataclass

class ForecastStrategy(Protocol):
    '''
    Method used to project / calculate future rates
    '''

    def forecast(self, data_series: Sequence[int | float], horizon: int) -> Sequence[float]:
        ...


@dataclass(frozen=True)
class HistoricalDriver:
    '''Holds the sequences of historical ratios '''
    revenue_growth: Sequence[float]
    ebit_margin: Sequence[float]
    capex_ratio: Sequence[float]
    da_ratio: Sequence[float]
    nwc_ratio: Sequence[float]

    latest_revenue: float | int
    latest_nwc: float | int