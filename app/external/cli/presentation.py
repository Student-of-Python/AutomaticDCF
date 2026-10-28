'''
app/external/cli/presentation.py
'''
from app.application.dto import CalculateDCFResponse
from app.domain.exceptions import Error
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

def format_money(amount: float) -> str:
    '''Formats large numbers into readable form'''

    if abs(amount) >= 1e9: #I should use this more often :D
        return f"${amount / 1e9:,.2f} B"
    elif abs(amount) >= 1e6:
        return f"${amount / 1e6:,.2f} M"
    elif abs(amount) >= 1e3:
        return f"${amount / 1e3:,.2f} K"
    return f"${amount:,.2f}"

def render_valuation(response: CalculateDCFResponse, console: Console | None = None) -> None:
    ''''''
    console = Console() if console is None else console
    upside = response.upside_downside_pct
    is_under = upside >= 0
    style = 'bold green' if is_under else 'bold red'
    text = 'UNDERVALUED' if is_under else 'OVERVALUED'
    border_color = 'green' if is_under else 'red'

    panel = Panel(
        f"[bold]Current Price:[/bold] ${response.current_price:,.2f}\n"
        f"[bold]Implied Fair Value:[/bold] ${response.implied_share_price:,.2f}\n"
        f"[bold]Upside / Downside:[/bold] [{style}]{upside:+.2%} ({text})[/{style}]\n"
        f"[bold]Cost of Capital (WACC):[/bold] {response.wacc:.2%}",
        title=f"[bold]DCF Valuation Summary: {response.ticker}[/bold]",
        border_style=border_color,
        expand=False
    )
    console.print(panel)

    val_table = Table(title="Enterprise & Equity Value Breakdown", box=box.ROUNDED)
    val_table.add_column("Valuation Component", style="cyan")
    val_table.add_column("Value", justify="right", style="bold")

    val_table.add_row("PV of Explicit Cash Flows", format_money(response.pv_fcff))
    val_table.add_row("PV of Terminal Value", format_money(response.pv_terminal_value))
    val_table.add_row("Enterprise Value (EV)", format_money(response.enterprise_value))
    val_table.add_row("Equity Value", format_money(response.equity_value))

    console.print(val_table)

    table = Table(
        title=f"{response.ticker} - Projected Cash Flows (FCFF)",
        box=box.ROUNDED,
        header_style="bold cyan"
    )
    table.add_column("Period", justify="center", style="dim")
    table.add_column("Projected FCFF", justify="right", style="green")

    for year, cf in enumerate(response.schedule.fcff, start=1):
        table.add_row(f"Year {year}", format_money(cf))

    console.print(table)


def render_error(error: Error, verbose: bool = False, console: Console | None = None) -> None:
    console = console or Console()
    console.print(Panel(f"[bold red]Valuation Failed:[/bold red] {error.msg}", border_style="red", expand=False))
    if verbose and error.details:
        console.print(f"[yellow]Details:[/yellow] {error.details}")
