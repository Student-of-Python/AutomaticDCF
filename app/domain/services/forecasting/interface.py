'''
app/domain/services/forecasting/ports.py
'''
from typing import Protocol, Sequence
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

class ForecastStrategy(Protocol):
    '''
    Method used to project / calculate future rates
    '''

    def forecast(self, data_series: Sequence[int | float], horizon: int) -> Sequence[float]:
        ...


@dataclass(frozen=True)
class HistoricalDriver:
    '''Holds the sequences of historical ratios '''
    revenue_growth: npt.NDArray[np.float32]
    ebit_margin: npt.NDArray[np.float32]
    capex_ratio: npt.NDArray[np.float32]
    da_ratio: npt.NDArray[np.float32]
    nwc_ratio: npt.NDArray[np.float32]
    latest_revenue: float | int
    latest_nwc: float | int

@dataclass(frozen=True)
class ProjectedCashFlowSchedule:
    revenues: list[float]
    ebits: list[float]
    capex: list[float]
    nopats: list[float]
    da: list[float]
    nwc: list[float]
    delta_nwc: list[float]
    fcff: list[float]

    @property
    def terminal_ebitda(self) -> float:
        '''Returns terminal ebidta'''
        return self.ebits[-1] + self.da[-1]