from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np
import pandas as pd
from DataScraper import Fundemental_Data

from typing import Optional

'''
Guide:
https://www.youtube.com/watch?v=nyot7FkYoqM
'''


class DCF(Fundemental_Data):
    def __init__(self, ticker, period = 5,income_stm = None, cash_flow_stm= None, cagr = None, **kwargs):
        super().__init__(ticker, period)
        self.ticker = ticker
        self.period = period
        assert self.period > 0

        #Set up neccesary statements
        income_statement_map = {
            'revenue': [
                'Revenue', 'TotalRevenue', 'Total revenue', 'Revenues', 'sales', 'totalSales'
            ],
            'ebitda': [
                'EBITDA', 'Ebitda', 'EarningsBeforeInterestTaxesDepreciationAmortization',
                'OperatingProfitBeforeDepreciation', 'OperatingIncomeBeforeDepreciation'
            ],
            'incomeTaxExpense': [
                'IncomeTaxExpense', 'Income Taxes', 'TaxProvision', 'ProvisionForIncomeTaxes',
                'IncomeTax', 'Taxes' ,'incomeTax', 'incomeTaxes', 'taxExpense', 'incomeTaxExpenseBenefit'],}
        cash_flow_map = {
            'depreciationAndAmortization': [
                'DepreciationAndAmortization', 'Depreciation Amortization',
                'Depreciation', 'Amortization', 'DA'
            ],
            'capitalExpenditure': [
                'CapitalExpenditure', 'Capital Expenditures', 'Capex', 'InvestmentsInPPE',
                'PurchasesOfPropertyAndEquipment'
            ],
            'freeCashFlow': [
                'FreeCashFlow', 'FCF', 'Free Cash Flow', 'CashFromOperations - Capex',
                'CashFlowFree'
            ],
        }

        self.WACC = self.calculate_WACC()
        self.CAGR = cagr if cagr else self.convert_percent_to_float((self.search_(
            f'CAGR {self.ticker} {self.get_similar_columns(self.general_info, ["industry"])} Projection', 'CAGR', amount=1, auto=True)))
        self.income_statement = income_stm if income_stm else self.normalize_columns(self.income_sheet, income_statement_map)
        self.cash_flow = cash_flow_stm if cash_flow_stm else self.normalize_columns(self.cash_sheet,cash_flow_map)

    def normalize_columns(self, df_original: pd.DataFrame, mapping_dict:dict):
        df = df_original.copy()
        df_columns = {column_name.lower(): column_name for column_name in df.columns}
        for key,value_list in  mapping_dict.items():
            found = False
            for value in value_list:
                if value.lower() in df_columns.keys():
                    df.rename(columns={
                        df_columns.get(value.lower()) : key
                    }, inplace = True)
                    found = True
                    break
            if not found:
                df.rename(columns={
                    self.get_most_similiar_word(key, df_columns) : key
                },inplace = True)
                print(f'Could not find replacement for {key}. Best guess is {self.get_most_similiar_word(key, df_columns)}')
        return df[[key for key in mapping_dict.keys()]]

    def project_category(self, dataframe_column: pd.DataFrame, terminal_rate: float | None, margin_coe: int = 1):
        values_df = pd.DataFrame(data = dataframe_column, columns=['values'])
        if terminal_rate:
            assert margin_coe <= len(dataframe_column) if margin_coe else True
            percent_last = values_df['values'].pct_change().to_list()[-margin_coe:]
            percent_last = sum(percent_last) / len(percent_last)






obj = DCF('TSM', 5, cagr=0.1, provider = 'sec')

obj.project_category(obj.income_statement['revenue'], terminal_rate=0.1)