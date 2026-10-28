'''
app/external/cli/main.py
'''

from app.domain.services.forecasting.forecaster import StrategyConfig
from app.infrastructure.company_data.yfinance_statements import YFinanceStatementsAdapter
from app.infrastructure.company_data.yfinance_profile import YFinanceProfileAdapter
from app.infrastructure.macro_data.composite import CompositeMacroAdapter
from app.application.dto import CalculateDCFRequest
from app.application.use_case import CalculateDCFUseCase
from app.external.cli.strategy_build import configure_strategies
import typer
from rich.console import Console


app = typer.Typer(help = "Automated Discount Cash FLow (DCF) Engine CLI")
console = Console()

def build_use_case(strategy_config: StrategyConfig) -> CalculateDCFUseCase:
    '''Builds use case'''
    return CalculateDCFUseCase(
        statement_adapter = YFinanceStatementsAdapter(),
        profile_adapter = YFinanceProfileAdapter(),
        macro_adapter = CompositeMacroAdapter(),
        strategy_config = strategy_config
    )

@app.command()
def dcf(
        ticker: str = typer.Argument(..., help="Stock ticker symbol (ex: AAPL)"),
        horizon: int = typer.Option(5, '--horizon', '-n', help = "Forecast horizon in years"),
        growth: float = typer.Option(0.025, "--growth", "-g", help = "Terminal growth rate of the company"),
        exit_multiple: float | None = typer.Option(None, '--multiple', '-m', help = "Exit multiple [OVERRIDE]"),
        risk_free: float | None = typer.Option(None, "--risk-free",'-r', help = 'Risk free rate [OVERRIDE]'),
        erp: float | None = typer.Option(None, "--erp", help  = 'Equity Risk Premium [OVERRIDE]'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help = 'Shows trace on errors'),
) -> None:
    strategy_config = configure_strategies(terminal_growth_rate = growth)

    request = CalculateDCFRequest(
        ticker = ticker,
        horizon = horizon,
        terminal_growth_rate = growth,
        exit_multiple = exit_multiple,
        risk_free_rate = risk_free,
        equity_risk_premium = erp
    )

    use_case = build_use_case(strategy_config)

    with console.status(f"[bold cyan]Fetching market data and valuing {ticker.upper()}..."):
        result = use_case.execute(request)


    if result.is_success:
        console.print(f"[bold green]Successfully valued {ticker.upper()}![/bold green]")
        console.print(f"Implied Price: ${result.value.implied_share_price:,.2f}")
        # (Later we will call render_report(result.value))
    else:
        console.print(f"[bold red]Valuation Failed:[/bold red] {result.error.msg}")
        raise typer.Exit(code=1)


