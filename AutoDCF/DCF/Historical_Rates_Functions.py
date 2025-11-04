import numpy as np
import pandas as pd
import random
import math


def format_percent_change(astype: str):
    """
    Decorator factory for automatically applying percent change transformation
    before executing a forecasting method.

    This ensures that the input data is first converted into percentage changes,
    which is the standard form for rate-based forecasting methods (e.g. growth rates).

    Args:
        astype (str): Determines whether to return the transformed data as a 'list' or 'numpy' array.

    Returns:
        callable: Decorator that preprocesses input data for wrapped functions.
    """
    def decorator(func):
        def wrapper(period, data, *args, **kwargs):
            # Convert to percent change before forecasting
            data = HistoricalRates.percent_change(data)
            if astype.lower() == 'list':
                data = list(data)
            return func(period, data, *args, **kwargs)
        return wrapper
    return decorator


class HistoricalRates:
    """
    Collection of static methods for generating historical and projected growth rate series.

    Each method simulates different behaviors in forecasting rates or returns:
        - Moving averages (simple, weighted, exponential)
        - Converging models (to a terminal rate)
        - Randomized or stochastic processes (Monte Carlo, Uniform)
        - Mean reversion dynamics (Ornstein–Uhlenbeck)
        - Linear transitions toward target rates

    These methods are designed to support DCF and financial modeling workflows.
    """

    @staticmethod
    def percent_change(data: pd.Series):
        """
        Computes the simple percentage change between consecutive data points.

        Args:
            data (pd.Series): Series or array-like of numerical values.

        Returns:
            np.ndarray: Array of percent changes, with the first value as 0.
        """
        data = data.to_numpy()
        diff = np.diff(data) / data[:-1]
        diff = diff[~np.isnan(diff)]
        diff = np.insert(diff, 0, 0)
        return diff

    @staticmethod
    @format_percent_change(astype='list')
    def MovingAverage(period: int, data: list, window: int):
        """
        Forecasts future rates using a simple moving average approach.

        Args:
            period (int): Number of periods to forecast.
            data (list): Historical rate series.
            window (int): Size of the trailing window for averaging.

        Returns:
            list: Extended data series with moving average forecasts.
        """
        assert window <= len(data)
        data_copy = data.copy()
        for i in range(period):
            select_years = data_copy[-window:]
            avg = sum(select_years) / window
            data_copy.append(avg)

        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy

    @staticmethod
    @format_percent_change(astype='list')
    def ConvergingMovingAverage(period: int, data, window: int, terminal_rate: float):
        """
        Computes moving averages that gradually converge toward a specified terminal rate.

        Args:
            period (int): Forecast horizon.
            data (list): Historical rate series.
            window (int): Size of the trailing window.
            terminal_rate (float): Target convergence rate.

        Returns:
            list: Forecasted rate series converging toward terminal_rate.
        """
        assert window <= len(data)
        assert terminal_rate
        data_copy = data.copy()
        for i in range(period):
            select_years = data_copy[-window:]
            avg = sum(select_years) / window

            alpha = (i + 1) / period
            avg = (1 - alpha) * avg + alpha * terminal_rate
            data_copy.append(avg)

        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy

    @staticmethod
    @format_percent_change(astype='list')
    def ExponentialMovingAverage(period: int, data, window: int, alpha: float = None):
        """
        Computes exponential moving averages (EMA) for future rates.

        Args:
            period (int): Forecast horizon.
            data (list): Historical rate series.
            window (int): Trailing window length.
            alpha (float, optional): Smoothing factor (default: 2/(window+1)).

        Returns:
            list: Forecasted rates using exponential weighting.
        """
        assert window <= len(data)
        data_copy = data.copy()
        alpha = alpha if alpha else 2 / (window + 1)
        for i in range(period):
            select_years = data_copy[-window:]
            local_avg = sum(select_years) / window
            ema = alpha * local_avg + (1 - alpha) * data_copy[-1]
            data_copy.append(ema)

        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy

    @staticmethod
    @format_percent_change(astype='list')
    def ConvergingExponentialMovingAverage(period: int, data, window: int, terminal_rate, alpha: float = None):
        """
        Forecasts exponential moving averages that converge toward a terminal rate.

        Args:
            period (int): Forecast horizon.
            data (list): Historical rate data.
            window (int): Number of trailing observations for EMA.
            terminal_rate (float): Target end-point rate.
            alpha (float, optional): Smoothing factor.

        Returns:
            list: Forecasted rate series converging to terminal_rate.
        """
        assert window <= len(data)
        assert terminal_rate
        data_copy = data.copy()
        alpha = alpha if alpha else 2 / (window + 1)
        for i in range(period):
            select_years = data_copy[-window:]
            local_avg = sum(select_years) / window
            ema = alpha * local_avg + (1 - alpha) * data_copy[-1]

            beta = (i + 1) / period
            ema = (1 - beta) * ema + beta * terminal_rate
            data_copy.append(ema)
        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy

    @staticmethod
    @format_percent_change(astype='list')
    def WeightedMovingAverage(period: int, data, window: int, weights: list):
        """
        Computes weighted moving averages where each value in the window is scaled by a weight.

        Args:
            period (int): Forecast horizon.
            data (list): Historical rate series.
            window (int): Window length for averaging.
            weights (list): Weight coefficients (ascending order recommended).

        Returns:
            list: Weighted moving average forecasts.
        """
        assert window <= len(data)
        assert window == len(weights)
        data_copy = data.copy()
        for i in range(period):
            select_years = data_copy[-window:]
            avg = sum([weight * rate for weight, rate in zip(weights, select_years)])
            data_copy.append(avg)
        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy

    @staticmethod
    @format_percent_change(astype='list')
    def ConvergingWeightedMovingAverage(period: int, data, window: int, weights: list, terminal_rate):
        """
        Forecasts weighted moving averages that converge to a target terminal rate.

        Args:
            period (int): Number of forecast periods.
            data (list): Historical rate series.
            window (int): Size of the averaging window.
            weights (list): Weight coefficients.
            terminal_rate (float): Target rate for convergence.

        Returns:
            list: Forecasted rates converging toward the terminal value.
        """
        assert window <= len(data)
        assert window == len(weights)
        data_copy = data.copy()
        for i in range(period):
            select_years = data_copy[-window:]
            avg = sum([weight * rate for weight, rate in zip(weights, select_years)])
            alpha = (i + 1) / period
            avg = (1 - alpha) * avg + alpha * terminal_rate
            data_copy.append(avg)
        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy

    @staticmethod
    @format_percent_change(astype='list')
    def MeanReverting(period: int, data, terminal_rate: float, phi: float = 0.7, kappa: float = 0.2):
        """
        Generates mean-reverting forecasts based on the Ornstein–Uhlenbeck process.

        Formula:
            R_{t+1} = R_t + φ(R_t - R_{t-1}) - κ(R_t - R_terminal)

        Args:
            period (int): Forecast horizon.
            data (list): Historical rate series.
            terminal_rate (float): Target long-term rate.
            phi (float): Momentum coefficient (acceleration term).
            kappa (float): Reversion strength toward terminal rate.

        Returns:
            list: Mean-reverted forecasted rate series.
        """
        assert len(data) >= 2
        data_copy = data.copy()
        for i in range(period):
            delta1 = data_copy[-1] - data_copy[-2]
            delta2 = data_copy[-1] - terminal_rate
            rate = data_copy[-1] + phi * delta1 - kappa * delta2
            data_copy.append(rate)
        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy

    @staticmethod
    @format_percent_change(astype='numpy')
    def LinearRate(period: int, data: pd.Series, terminal_rate: float):
        """
        Produces a linear rate trajectory between the last data point and terminal rate.

        Args:
            period (int): Forecast horizon.
            data (pd.Series): Historical rate series.
            terminal_rate (float): End target rate.

        Returns:
            np.ndarray: Linearly interpolated rate values.
        """
        data_copy = data.copy()
        arr = np.linspace(data_copy[-1], terminal_rate, period)
        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return arr

    @staticmethod
    @format_percent_change(astype='numpy')
    def Uniform(period: int, data, max_randomness: float = 0):
        """
        Applies uniform random variation around the last observed rate for forecasting.

        Args:
            period (int): Number of forecast periods.
            data (array-like): Historical rate series.
            max_randomness (float): Maximum random deviation (e.g., 0.1 = ±10%).

        Returns:
            np.ndarray: Forecasted values with uniform random variation.
        """
        data_copy = data.copy()
        rand_arr = data[-1] * (1 + np.random.uniform(-max_randomness, max_randomness, period))
        full_data = np.hstack((data_copy, rand_arr))
        assert len(full_data) == len(data) + period, f"[ERROR] Mismatch in Size: {len(full_data)} != {len(data) + period}"
        return full_data

    @staticmethod
    @format_percent_change(astype='numpy')
    def MonteCarlo(period: int, data, percentile: float = 0.9, sigma: float = None, episodes: int = 100):
        """
        Monte Carlo simulation for stochastic rate forecasting.

        Each step generates multiple random paths based on historical mean and variance,
        then selects a percentile-based outcome as the forecasted rate.

        Args:
            period (int): Forecast horizon.
            data (array-like): Historical data.
            percentile (float): Percentile used for outcome selection (default 0.9).
            sigma (float, optional): Standard deviation; computed if None.
            episodes (int): Number of Monte Carlo iterations.

        Returns:
            np.ndarray: Forecasted rate trajectory using stochastic sampling.
        """
        data_copy = data.copy()
        for i in range(period):
            mean = float(np.mean(data_copy))
            sigma = math.sqrt(np.var(data_copy)) if not sigma else sigma
            samples = [random.gauss(mean, sigma) for _ in range(episodes)]
            change_rate = [data_copy[-1] * (1 + rate_of_change) for rate_of_change in samples]
            forecast_value = np.percentile(change_rate, percentile * 100)
            data_copy = np.append(data_copy, forecast_value)
        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy

    @staticmethod
    @format_percent_change(astype='numpy')
    def ConvergingMonteCarlo(period: int, data, terminal_rate: float, percentile: float = 0.9, sigma: float = None, episodes: int = 100):
        """
        Monte Carlo simulation variant with gradual convergence to a terminal rate.

        Args:
            period (int): Forecast horizon.
            data (array-like): Historical data.
            terminal_rate (float): Target end-point rate for convergence.
            percentile (float): Percentile threshold for stochastic sampling.
            sigma (float, optional): Standard deviation; auto-computed if None.
            episodes (int): Number of random simulation runs.

        Returns:
            np.ndarray: Forecasted series converging toward the terminal rate.
        """
        assert terminal_rate
        data_copy = data.copy()

        for i in range(period):
            mean = float(np.mean(data_copy))
            sigma = math.sqrt(np.var(data_copy)) if not sigma else sigma
            samples = [random.gauss(mean, sigma) for _ in range(episodes)]
            change_rate = [data_copy[-1] * (1 + rate_of_change) for rate_of_change in samples]
            forecast_value = np.percentile(change_rate, percentile * 100)

            alpha = (i + 1) / period
            forecast_value = (1 - alpha) * forecast_value + alpha * terminal_rate
            data_copy = np.append(data_copy, forecast_value)

        assert len(data_copy) == len(data) + period, f"[ERROR] Mismatch in Size: {len(data_copy)} != {len(data) + period}"
        return data_copy
