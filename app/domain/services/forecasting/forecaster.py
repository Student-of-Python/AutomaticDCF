'''
app/domain/services/forecasting/forecaster.py
'''
from .interface import ProjectedCashFlowSchedule, ForecastStrategy,HistoricalDriver
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class StrategyConfig:
    '''
        Strategies

    '''
    revenue_strat: ForecastStrategy
    capex_strat: ForecastStrategy
    ebit_strat: ForecastStrategy
    da_strat: ForecastStrategy
    nwc_strat: ForecastStrategy


'''
TODO:
Write a config class for cash flow forecaster
implement the logic in cash flow forecaster. 
'''

class CashFlowForecaster:
    def __init__(self, config: StrategyConfig):
        self._config = config

    def project(self, driver: HistoricalDriver, tax_rate: float, horizon: int = 3) -> ProjectedCashFlowSchedule:
        ''''''
        future_growth = np.array(self._config.revenue_strat.forecast(driver.revenue_growth, horizon= horizon))
        future_ebit_margins = np.array(self._config.ebit_strat.forecast(driver.ebit_margin, horizon=horizon))
        future_capex_ratios = np.array(self._config.capex_strat.forecast(driver.capex_ratio, horizon=horizon))
        future_da_ratio = np.array(self._config.da_strat.forecast(driver.da_ratio, horizon=horizon))
        future_nwc_ratio = np.array(self._config.nwc_strat.forecast(driver.nwc_ratio, horizon=horizon))



        revenue_proj = driver.latest_revenue * np.cumprod(future_growth + 1)
        ebit_proj = revenue_proj * future_ebit_margins
        nopat_proj = ebit_proj * (1 - tax_rate)
        da_proj = revenue_proj * future_da_ratio
        capex_proj = revenue_proj * future_capex_ratios
        nwc_proj = revenue_proj * future_nwc_ratio
        delta_nwc_proj = np.diff(np.concatenate(([driver.latest_nwc], nwc_proj)))

        fcff_proj = nopat_proj + da_proj - capex_proj - delta_nwc_proj

        return ProjectedCashFlowSchedule(
            revenues = revenue_proj.tolist(),
            ebits = ebit_proj.tolist(),
            capex = capex_proj.tolist(),
            nopats = nopat_proj.tolist(),
            da = da_proj.tolist(),
            nwc = nwc_proj.tolist(),
            delta_nwc = delta_nwc_proj.tolist(),
            fcff = fcff_proj.tolist(),
        )
