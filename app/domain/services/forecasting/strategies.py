'''
app/domain/services/forecasting/strategies.py
'''
from app.domain.exceptions import EmptyDataSeriesError
from typing import Sequence
import numpy as np

class HistoricalAverageForecast:
    '''

    This forecast type takes the average of the series, and then maps it out to each value in the future series.

    '''

    def __init__(self, window: int | None = None):
        '''
        :param window: option for window average
        '''
        if window is not None and window <= 0:
            raise ValueError(f"Window must be a positive integer, got {window}")
        self._window = window

    def forecast(self, data_series: Sequence[int | float], horizon: int = 3) -> list[float]:
        ''''''
        if len(data_series) == 0:
            raise EmptyDataSeriesError(f"Series Data has no data points. Cannot forecast on no data.")
        if horizon <= 0:
            raise ValueError(f"Horizon must be a positive integer")

        rolling = data_series[-self._window:] if self._window else data_series
        avg = float(np.mean(rolling))
        return [avg] * horizon

class RollingAverageForecast:
    '''Rolling average -> take average of sliding window until horizon'''


    def __init__(self, window: int | None = None):
        if window is not None and window <= 0:
            raise ValueError(f"Window must be a positive integer, got {window}")
        self._window = window



    def forecast(self,  data_series: Sequence[int | float], horizon: int = 3) -> list[float]:
        ''''''
        if len(data_series) == 0:
            raise EmptyDataSeriesError(f"Series Data has no data points. Cannot forecast on no data.")
        if horizon <= 0:
            raise ValueError(f"Horizon must be a positive integer")

        forecast = []
        working = list(data_series)

        for _ in range(horizon):
            window_data = working[-self._window:] if self._window else working
            next_val = float(np.mean(window_data))
            working.append(next_val)
            forecast.append(next_val)

        return forecast

class LinearConvergenceForecast:

    def __init__(self, terminal_rate: float):
        self._terminal_rate = terminal_rate

    def forecast(self, data_series: Sequence[int | float], horizon: int = 3) -> list[float]:
        ''''''
        if len(data_series) == 0:
            raise EmptyDataSeriesError(f"Series Data has no data points. Cannot forecast on no data.")
        if horizon <= 0:
            raise ValueError(f"Horizon must be a positive integer")

        return np.linspace(data_series[-1], self._terminal_rate, horizon + 1)[1:].tolist()

