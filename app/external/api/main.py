'''
app/external/api/main.py
'''
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.application.dto import CalculateDCFRequest
from app.application.use_case import CalculateDCFUseCase
from app.domain.services.forecasting.forecaster import StrategyConfig
from app.domain.services.forecasting.strategies import HistoricalAverageForecast
from app.infrastructure.company_data.yfinance_statements import YFinanceStatementsAdapter
from app.infrastructure.company_data.yfinance_profile import YFinanceProfileAdapter
from app.infrastructure.macro_data.composite import CompositeMacroAdapter
from app.infrastructure.macro_data.erp_provider import DamodaranERPProvider
from app.infrastructure.macro_data.yield_provider import TradingEconomicsYieldProvider
from app.external.api.request import ValuationRequest, create_driver_strategy
from app.external.export.excel_generator import ExcelReportGenerator

app = FastAPI(title="DCF Valuation Engine API", version="1.0.0")

# Allows browsers to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parents[3]
FRONTEND_DIR = ROOT_DIR / "frontend"

# Mount static assets (CSS, images, etc.)
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
if (ROOT_DIR / "img").exists():
    app.mount("/img", StaticFiles(directory=ROOT_DIR / "img"), name="img")

@app.get("/")
def get_home_page():
    """Serves the Home overview page."""
    home_file = FRONTEND_DIR / "home.html"
    if not home_file.exists():
        raise HTTPException(status_code=404, detail="home.html not found")
    return FileResponse(home_file)

@app.get("/valuation")
def get_valuation_page():
    """Serves the Valuation Terminal page."""
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_file)

@app.get("/theory")
def get_theory_page():
    """Serves the Theory & Methodology paper."""
    theory_file = FRONTEND_DIR / "theory.html"
    if not theory_file.exists():
        raise HTTPException(status_code=404, detail="theory.html not found")
    return FileResponse(theory_file)


def build_use_case(strategy_config: StrategyConfig) -> CalculateDCFUseCase:
    """Helper factory for assembling dependencies."""
    macro_adapter = CompositeMacroAdapter(
        yield_provider=TradingEconomicsYieldProvider(),
        equity_provider=DamodaranERPProvider()
    )
    return CalculateDCFUseCase(
        statement_adapter=YFinanceStatementsAdapter(),
        profile_adapter=YFinanceProfileAdapter(),
        macro_adapter=macro_adapter,
        strategy_config=strategy_config
    )

@app.post("/api/v1/valuation")
def calculate_valuation(external_request: ValuationRequest):
    """
    Receives JSON request, executes DCF Use Case, and returns JSON results.
    """
    try:
        request = CalculateDCFRequest(
            ticker=external_request.ticker,
            horizon=external_request.horizon,
            terminal_growth_rate=external_request.growth,
            exit_multiple=external_request.exit_multiple,
            risk_free_rate=external_request.risk_free,
            equity_risk_premium=external_request.erp
        )
        strategy_config = StrategyConfig(
            revenue_strat=create_driver_strategy(external_request.revenue_strat, default_target=external_request.growth),
            ebit_strat=create_driver_strategy(external_request.ebit_strat),
            capex_strat=create_driver_strategy(external_request.capex_strat),
            da_strat=create_driver_strategy(external_request.da_strat),
            nwc_strat=create_driver_strategy(external_request.nwc_strat),
        )

    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    use_case = build_use_case(strategy_config)
    result = use_case.execute(request=request)

    if result.is_success:
        return {
            'ticker': result.value.ticker,
            'current_price': result.value.current_price,
            'implied_share_price': result.value.implied_share_price,
            'upside_downside_pct': result.value.upside_downside_pct,
            'wacc': result.value.wacc,
            'enterprise_value': result.value.enterprise_value,
            'equity_value': result.value.equity_value,
            'pv_fcff': result.value.pv_fcff,
            'pv_terminal_value': result.value.pv_terminal_value,
            'projected_fcff': list(result.value.schedule.fcff)
        }
    else:
        raise HTTPException(status_code=400, detail=result.error.msg)

@app.post("/api/v1/export/excel")
def export_excel_model(external_request: ValuationRequest):
    """
    Executes DCF valuation with the requested strategy parameters and returns
    a formatted multi-sheet Excel model (.xlsx) as a file download.
    """
    try:
        request = CalculateDCFRequest(
            ticker=external_request.ticker,
            horizon=external_request.horizon,
            terminal_growth_rate=external_request.growth,
            exit_multiple=external_request.exit_multiple,
            risk_free_rate=external_request.risk_free,
            equity_risk_premium=external_request.erp
        )
        strategy_config = StrategyConfig(
            revenue_strat=create_driver_strategy(external_request.revenue_strat, default_target=external_request.growth),
            ebit_strat=create_driver_strategy(external_request.ebit_strat),
            capex_strat=create_driver_strategy(external_request.capex_strat),
            da_strat=create_driver_strategy(external_request.da_strat),
            nwc_strat=create_driver_strategy(external_request.nwc_strat),
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    use_case = build_use_case(strategy_config)
    result = use_case.execute(request=request)

    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.error.msg)

    xlsx_bytes = ExcelReportGenerator.generate(result.value, request)
    filename = f"{result.value.ticker.upper()}_DCF_Valuation_Model.xlsx"

    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
