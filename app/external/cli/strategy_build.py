'''
app/external/cli/strategy_build.py
'''
from app.domain.services.forecasting.strategies import (HistoricalAverageForecast, RollingAverageForecast, LinearConvergenceForecast)
from app.domain.services.forecasting.forecaster import StrategyConfig
from app.domain.services.forecasting.interface import ForecastStrategy
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, FloatPrompt

console = Console()



def prompt_strategy_for(metric_name: str, default_target_rate: float | None = None ) -> ForecastStrategy:
    """Prompts the user to configure a forecasting strategy."""
    console.print(f"\n[bold cyan]Configure strategy for:[/bold cyan] [yellow]{metric_name}[/yellow]")

    console.print(f"  [bold]\\[1][/bold] Historical Average")
    console.print(f"  [bold]\\[2][/bold] Rolling Average")
    console.print(f"  [bold]\\[3][/bold] Linear Convergence")

    choice = Prompt.ask(
        f"Select Strategy for {metric_name}",
        choices=["1", "2", "3"],
        default="1"
    )

    if choice == "1":
        window = IntPrompt.ask("Enter window size in years (-1 for all)", default=-1)
        return HistoricalAverageForecast(window) if window > 0 else HistoricalAverageForecast()

    elif choice == "2":
        window = IntPrompt.ask("Enter window size in years (-1 for all)", default=-1)
        return RollingAverageForecast(window=window) if window > 0 else RollingAverageForecast()

    else:
        if default_target_rate is not None:
            rate = FloatPrompt.ask("Enter Target Rate", default=default_target_rate)
        else:
            rate = FloatPrompt.ask("Enter Target Rate", default=default_target_rate)
        return LinearConvergenceForecast(terminal_rate=rate)

def configure_strategies(terminal_growth_rate: float) -> StrategyConfig:
    ''''''
    console.print(f"  [bold]\\[1][/bold] Quick Default (Historical Average for all metrics)")
    console.print(f"  [bold]\\[2][/bold] Custom (Configure each metric)")

    choice = Prompt.ask(
        f"Select Choice",
        choices=["1", "2"],
        default= "1"
    )

    if choice == "1":
        return StrategyConfig(
            revenue_strat = HistoricalAverageForecast(),
            capex_strat = HistoricalAverageForecast(),
            ebit_strat = HistoricalAverageForecast(),
            da_strat = HistoricalAverageForecast(),
            nwc_strat = HistoricalAverageForecast(),)

    else:
        return StrategyConfig(
            revenue_strat = prompt_strategy_for('Revenue Growth', default_target_rate=terminal_growth_rate),
            ebit_strat=prompt_strategy_for('Ebit Margin'),
            capex_strat = prompt_strategy_for('Capex Ratio'),
            da_strat = prompt_strategy_for('D&A Ratio'),
            nwc_strat = prompt_strategy_for('NWC Ratio')
        )