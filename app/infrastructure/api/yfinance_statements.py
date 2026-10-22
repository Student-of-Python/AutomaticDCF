'''
app\infrastructure\api\yfinance_data.py
'''
from app.domain.enums import IncomeStatementCols, CashStatementCols, BalanceSheetCols
from app.interface.statements_interface import StatementAdapter
from pandas import DataFrame
import yfinance as yf




class YFinanceStatementsAdapter(StatementAdapter):
    '''
    Notes: Yahoofinance limited to only 4 years historical -- not bad for MVP, but may need to extend later on.

    '''


    def __init__(self, ticker: str):
        self._ticker = yf.Ticker(ticker=ticker)
        #TODO: Add years back later? For now, sticking to 4 years.

    def _get_cash(self) -> DataFrame:
        '''
        
        :return: 
        
        '''
        return self._ticker.cash_flow.T


    def _get_balance(self) -> DataFrame:
        '''
            
        '''
        return self._ticker.balance_sheet.T

    def _get_income(self) -> DataFrame:
        '''

        :return:
        '''
        return self._ticker.income_stmt.T

    @property
    def _income_mapping(self) -> dict[str, str]:
        return {
        'Total Revenue': IncomeStatementCols.REVENUE,
        'EBITDA': IncomeStatementCols.EBITDA,
        'EBIT': IncomeStatementCols.EBIT,
    }

    @property
    def _balance_mapping(self) -> dict[str, str]:
        return {
        'Stockholders Equity': BalanceSheetCols.TOTAL_EQUITY,
        'Total Debt': BalanceSheetCols.TOTAL_DEBT,
        'Current Assets': BalanceSheetCols.TOTAL_CURRENT_ASSETS,
        'Current Liabilities': BalanceSheetCols.TOTAL_CURRENT_LIABILITIES,
        'Cash And Cash Equivalents': BalanceSheetCols.CASH_ON_HAND,
    }

    @property
    def _cash_mapping(self) -> dict[str, str]:
        return {
        'Depreciation And Amortization': CashStatementCols.DEPRECIATION,
        'Capital Expenditure': CashStatementCols.CAPEX,
        'Operating Cash Flow': CashStatementCols.CASH_OPERATING,
    }

