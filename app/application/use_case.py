'''
app/application/use_case.py
'''
from app.domain.services.valuation import ValuationCalculator
from app.domain.services.forecasting.forecaster import CashFlowForecaster
from app.domain.services.forecasting.analyzer import HistoricalDriverAnalyzer
from app.domain.services.wacc import WaccCalculator
from app.domain.services.forecasting.forecaster import StrategyConfig #I need to change this import
from app.interface import StatementAdapter, MacroAdapter, ProfileAdapter
from .dto import CalculateDCFRequest, CalculateDCFResponse
from app.domain.exceptions import ErrorCode, Error
from app.domain.entities import Result
from dataclasses import dataclass

@dataclass(frozen = True)
class CalculateDCFUseCase:
    statement_adapter: StatementAdapter
    profile_adapter: ProfileAdapter
    macro_adapter: MacroAdapter
    strategy_config: StrategyConfig

    def execute(self, request: CalculateDCFRequest) -> Result[CalculateDCFResponse]:
        '''Executes dcf logic'''

        statements = self.statement_adapter.get_statements(request.ticker) # I need to make ticker a parameter --> stateless

        if not statements.is_success:
            return Result.failed(error = statements.error)

        profile = self.profile_adapter.get_profile(request.ticker)

        if not profile.is_success:
            return Result.failed(error = profile.error)

        macro_vars = self._resolve_macro_rates(request=request, country = profile.value.country)

        if not macro_vars.is_success:
            return Result.failed(error = macro_vars.error)

        risk_free_rate, equity_premium_rate = macro_vars.value

        exit_multiple = request.exit_multiple if request.exit_multiple is not None else profile.value.ev_ebitda_multiple

        try:
            wacc_calcs = WaccCalculator(
                risk_free_rate = risk_free_rate,
                equity_premium = equity_premium_rate,
                beta = profile.value.beta,
                total_debt = statements.value.latest_total_debt,
                total_equity = statements.value.latest_total_equity,
                interest_expense = statements.value.latest_interest_expense,
                tax_rate = statements.value.effective_tax_rate() #Need to pass in default tax rate?
            )
        except Exception as err:
            return Result.failed(error=Error.invalid_data(msg = str(err), details={})) #Add more details?

        historical_analysis = HistoricalDriverAnalyzer.analyze(statements = statements.value)

        future_projections = CashFlowForecaster(config = self.strategy_config).project(driver = historical_analysis,
                                                                                       tax_rate= statements.value.effective_tax_rate(),
                                                                                       horizon = request.horizon)
        try:
            val = ValuationCalculator(
                fcffs = future_projections.fcff,
                terminal_ebitda = future_projections.terminal_ebitda,
                wacc = wacc_calcs.wacc,
                cash = statements.value.latest_cash_and_equivalents,
                total_debt = statements.value.latest_total_debt,
                shares_outstanding = profile.value.shares_outstanding,
                terminal_growth_rate = request.terminal_growth_rate,
                exit_multiple = exit_multiple

            )
        except Exception as err:
            return Result.failed(error=Error.invalid_data(msg=str(err), details={}))  # Add more details?

        return Result.success(result = CalculateDCFResponse(
            ticker = request.ticker,
            current_price = profile.value.current_price,
            implied_share_price = val.implied_share_price,
            wacc = wacc_calcs.wacc,
            enterprise_value = val.enterprise_value,
            equity_value = val.equity_value,
            pv_fcff = val.pv_fcff,
            pv_terminal_value = val.pv_terminal_value,
            schedule = future_projections
        ))


    def _resolve_macro_rates(self, request: CalculateDCFRequest, country: str) -> Result[tuple[float,float]]:
        ''''''
        risk_free_rate = request.risk_free_rate
        equity_premium_rate = request.equity_risk_premium

        if risk_free_rate is None or equity_premium_rate is None:
            macro_result = self.macro_adapter.get_macro(country)
            if not macro_result.is_success:
                return Result.failed(error=macro_result.error)

            if risk_free_rate is None:
                risk_free_rate = macro_result.value.risk_free_rate
            if equity_premium_rate is None:
                equity_premium_rate = macro_result.value.equity_premium_rate

        return Result.success(result = (risk_free_rate, equity_premium_rate))