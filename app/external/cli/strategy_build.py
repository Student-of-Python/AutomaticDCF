'''
app/external/cli/strategy_build.py
'''
from app.domain.services.forecasting.strategies import (HistoricalAverageForecast, RollingAverageForecast, LinearConvergenceForecast)
from app.domain.services.forecasting.forecaster import StrategyConfig
from app.domain.services.forecasting.interface import ForecastStrategy
from app.domain.enums import StrategyChoice, MetricName
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, FloatPrompt

console = Console()


def prompt_strategy_for(metric_name: MetricName, default_target_rate: float) -> ForecastStrategy:
    """Prompts the user to configure a forecasting strategy."""
    console.print(f"\n[bold cyan]Configure strategy for:[/bold cyan] [yellow]{metric_name.value}[/yellow]")

    console.print(f"  [bold]\\[1][/bold] {StrategyChoice.HISTORICAL_AVG.value}")
    console.print(f"  [bold]\\[2][/bold] {StrategyChoice.ROLLING_AVG.value}")
    console.print(f"  [bold]\\[3][/bold] {StrategyChoice.LINEAR_CONV.value}")

    choice = Prompt.ask(
        f"Select Strategy for {metric_name.value}",
        choices=["1", "2", "3"],
        default="1"
    )

    if choice == "1":
        window = IntPrompt.ask("Enter window size in years (-1 for all)", default=-1)
        return HistoricalAverageForecast(window) if window > 0 else HistoricalAverageForecast()

    elif choice == "2":
        window = IntPrompt.ask("Enter window size in years", default=3)
        return RollingAverageForecast(window=window)

    else:
        rate = FloatPrompt.ask("Enter Target Rate", default=default_target_rate)
        return LinearConvergenceForecast(terminal_rate=rate)