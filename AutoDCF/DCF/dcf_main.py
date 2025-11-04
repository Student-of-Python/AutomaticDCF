from AutoDCF.DCF.Historical_Rates_Functions import HistoricalRates
from AutoDCF.DataPipeline.helper import manual_init
from AutoDCF.DataPipeline.prepare_data import PrepareData
from typing import Union, Optional, List
import numpy as np
import pandas as pd
import os


class DCF(PrepareData):
    """
    Discounted Cash Flow (DCF) analysis class.

    This class automates the construction of a DCF valuation model by forecasting
    future financial statements, computing unlevered free cash flows, discounting
    them to present value, and deriving an estimated share price using either
    the perpetuity or exit multiple methods.

    Inherits:
        PrepareData: Base class responsible for preparing and cleaning input financial data.

    Attributes:
        manual_input (dict): User-provided configuration for DCF inputs.
        ticker (str): Stock ticker symbol.
        historical_period (int): Number of years of historical data to use.
        period (int): Number of years to forecast into the future.
        wacc (float): Weighted Average Cost of Capital.
        terminal_rate (float): Terminal growth rate (CAGR).
        dcf (pd.DataFrame): Processed DataFrame containing income, cash flow, and balance sheet data.
        ev_ebidta_mode (str): Mode for EV/EBITDA multiple calculation ('basket', etc.).
        industry (str): Industry classification.
        rate_map (dict): Mapping of data columns to forecasting methods/rates.
        method (str): Valuation approach ('perpetuity' or 'exit_multiple').
        export (bool): Whether to export the results to Excel.
        price (Optional[float]): Calculated share price.
    """

    @staticmethod
    def get_auto_rates(period: int, data: List[Union[float, int, None]], rate_type: str, params: dict) -> Optional[pd.Series]:
        """
        Dynamically fetches and executes a rate calculation function from HistoricalRates.

        Args:
            period (int): Number of forecasted periods.
            data (List[Union[float, int, None]]): Historical or partially forecasted data series.
            rate_type (str): Name of the rate calculation function within HistoricalRates.
            params (dict): Parameters to pass into the rate function.

        Returns:
            Optional[pd.Series]: Calculated rate series for the specified period.
        """
        assert isinstance(rate_type, str), f'[ERROR] rate_type object (type {type(rate_type)}) is not type str'
        assert isinstance(params, dict), f'[ERROR] params object (type {type(params)}) is not type dict'
        assert hasattr(HistoricalRates, rate_type), f'[ERROR] HistoricalRates has no attribute {rate_type}'
        rate_func = getattr(HistoricalRates, rate_type)
        return rate_func(period, data, **params)

    @manual_init
    def __init__(self, **kwargs):
        """
        Initializes the DCF model instance.

        Args:
            **kwargs: Arbitrary keyword arguments passed from user input or pipeline.

        Raises:
            AssertionError: If historical or forecast periods are invalid.
        """
        self.manual_input = kwargs.get('manual_input')
        self.ticker = str(self.manual_input.get('Ticker', None)).upper()
        self.historical_period = int(self.manual_input.get('Historical_Period', None))
        self.period = int(self.manual_input.get('Forecasted_Period', None))
        assert self.period >= 1, f'[ERROR] forecast_period {self.period} >=! 1'
        assert self.historical_period >= 1, f'[ERROR] historical_period {self.historical_period} >=! 1'
        super().__init__(self.ticker, self.historical_period, manual_input=kwargs.get('manual_input'))
        '''
        Parameters:
            ticker (str): Equity symbol.
            historical_period (int): Years back to consider for historical data.
            forecast_period (int): Number of years to forecast forward.
            mode (str): Methodology to forecast (Options: 'historical', 'exponential', 'manual').
            kwargs:
                assumption_table (dict): Manual assumption table, if applicable.
        '''

        # Initialize core variables
        self.wacc = self.calculate_wacc()
        self.terminal_rate = self.get_cagr()

        # Prepare data for DCF model
        self.dcf = self.prepare_data_for_dcf()

        # Configuration inputs from kwargs
        self.ev_ebidta_mode = str(self.manual_input.get('ev_ebidta_multiple_mode', 'basket'))
        self.industry = str(self.manual_input.get('industry', 'industry'))
        self.rate_map = dict(self.manual_input.get('rate_map', None))
        self.method = str(self.manual_input.get('Method', 'perpetuity'))
        self.export = bool(self.manual_input.get('Export', False))
        self.price = None

        # Run share price calculation
        self.calculate_share_price()

    def update_category(self, column_name: str):
        """
        Updates a DCF data column with forecasted values based on cumulative growth rates.

        Args:
            column_name (str): The name of the column in the DCF DataFrame to update.

        Returns:
            None
        """
        cum_prod_rates = np.cumprod((self.dcf[f'{column_name}_rates'][-self.period:].to_numpy() + 1))
        cum_prod_rates *= float(self.dcf[column_name].iloc[self.historical_period - 1].item())
        cum_prod_series = pd.Series(cum_prod_rates, index=list(self.dcf.index)[-self.period:])
        self.dcf[column_name] = self.dcf[column_name].fillna(cum_prod_series)

    def forcast_categories(self):
        """
        Forecasts all financial categories in the DCF model based on the rate mapping configuration.

        Handles three modes:
            - 'auto': Uses historical rates and internal functions to compute future values.
            - 'hybrid': Combines manual inputs with auto-calculated extensions.
            - 'manual': Uses fully manual user-provided rate lists.

        Returns:
            None
        """
        for column in self.dcf.columns:
            rate_mapping = self.rate_map.get(column, None)

            if not rate_mapping:
                print(f'[ERROR] {column} does not exist in dcf column {self.dcf.columns}')
                continue

            mode = str(rate_mapping.get('mode')).lower()

            # Auto mode: fully computed by HistoricalRates functions
            if mode == 'auto':
                rate_type = rate_mapping.get('auto_method', None)
                params = rate_mapping.get('parameters', None)
                if params.get('terminal_rate') in ('Auto', 'auto', 'AUTO'):
                    params['terminal_rate'] = self.terminal_rate
                self.dcf[f'{column}_rates'] = self.get_auto_rates(self.period, self.dcf[column], rate_type, params)

            # Hybrid mode: part manual, part auto
            elif mode == 'hybrid':
                manual_rates = rate_mapping.get('manual_rates', None)
                auto_fill = rate_mapping.get('auto_method', None)
                params = rate_mapping.get('parameters', None)
                assert isinstance(manual_rates, list), f'[ERROR] Manual input is not correct datatype: {type(manual_rates)} != List'
                assert len(manual_rates) < self.period, f'[ERROR] Mismatch in manual input length: {len(manual_rates)} !< {self.period}'
                assert all([isinstance(rate, (int, float)) for rate in manual_rates]), f'[ERROR] Invalid Data Type in manual input'
                assert isinstance(auto_fill, str), f'[ERROR] auto_fill input is not correct datatype: {type(auto_fill)} != str'
                assert isinstance(params, dict), f'[ERROR] params input is not correct datatype: {type(params)} != dict'

                if params.get('terminal_rate') in ('Auto', 'auto', 'AUTO'):
                    params['terminal_rate'] = self.terminal_rate

                diff = self.period - len(manual_rates)
                manual_rates.extend([np.nan] * diff)
                self.dcf[f'{column}_rates'] = list(HistoricalRates.percent_change(self.dcf[column])) + manual_rates
                self.update_category(column)
                self.dcf[f'{column}_rates'] = self.get_auto_rates(diff, self.dcf[column], auto_fill, params)

            # Manual mode: uses only user-provided rates
            elif mode == 'manual':
                manual_rates = rate_mapping.get('manual_rates', None)
                assert isinstance(manual_rates, list), f'[ERROR] Manual input is not correct datatype: {type(manual_rates)} != List'
                assert len(manual_rates) == self.period, f'[ERROR] Mismatch in manual input length: {len(manual_rates)} != {self.period}'
                assert all([isinstance(rate, (int, float)) for rate in manual_rates]), f'[ERROR] Invalid Data Type in manual input'
                self.dcf[f'{column}_rates'] = list(HistoricalRates.percent_change(self.dcf[column])) + manual_rates

            self.update_category(column)
        assert not self.dcf.isnull().values.any(), f'[ERROR] Detected NaN Values in DCF: {self.dcf}'

    def get_future_fcf(self):
        """
        Computes unlevered and present value free cash flows for each forecasted period.

        Uses:
            Unlevered Cash Flow = NOPAT + D&A - CAPEX - ΔNWC
            Present Value = UCF / (1 + WACC) ** year

        Returns:
            None
        """
        missing = {'nopat', 'da', 'capex', 'nwc'} - set(self.dcf.columns)
        assert not missing, f"[ERROR] Missing required columns: {missing}"

        self.dcf['delta_nwc'] = self.dcf['nwc'].diff()
        self.dcf['Unlevered_CashFlow'] = (
            self.dcf['nopat'] +
            self.dcf['da'] -
            abs(self.dcf['capex']) -
            self.dcf['delta_nwc'].fillna(0)
        )

        present_cash_flows = self.dcf['Unlevered_CashFlow'][-self.period:] / [(1+self.wacc) ** year for year in range(1, self.period+1)]
        padding = len(self.dcf.index) - len(present_cash_flows)
        present_cash_flow_series = pd.Series([0] * padding + present_cash_flows.to_list(), index=self.dcf.index)
        self.dcf['Present_CashFlow'] = present_cash_flow_series

    def exit_multiple_method(self) -> float:
        """
        Calculates share price using the Exit Multiple valuation method.

        Formula:
            Terminal Value = Exit_Multiple * (Last_DA + Last_EBIT)
            Present TV = Terminal Value / (1 + WACC) ** Years
            EV = Σ(Present Value of FCF) + Present TV
            Equity Value = EV - Net Debt
            Share Price = Equity / Shares Outstanding

        Returns:
            float: Estimated share price.
        """
        da = self.dcf['da'].iloc[-1].item()
        ebit = self.dcf['ebit'].iloc[-1].item()
        net_debt = float(self.balance_sheet['netDebt'].iloc[0].item())

        exit_multiple = self.get_ev_ebidta_multiple(mode=self.ev_ebidta_mode, industry=self.industry)
        terminal_value = (float(da + ebit)) * exit_multiple
        present_terminal_value = terminal_value / (1+self.wacc) ** self.period
        enterprise_value = sum(self.dcf['Present_CashFlow'].iloc[self.period:]) + present_terminal_value
        equity = enterprise_value - net_debt
        return float(equity / self.get_shares_outstanding())

    def perpetuity_method(self) -> float:
        """
        Calculates share price using the Perpetuity Growth valuation method.

        Formula:
            Terminal Value = Last_UFCF * (1 + g) / (WACC - g)
            Present TV = TV / (1 + WACC) ** Years
            EV = Σ(Present Value of FCF) + Present TV
            Equity Value = EV - Net Debt
            Share Price = Equity / Shares Outstanding

        Returns:
            float: Estimated share price.
        """
        assert self.wacc > self.terminal_rate, f'[ERROR] WACC must be greater than Terminal Rate: {self.wacc} >! {self.terminal_rate}'
        net_debt = float(self.balance_sheet['netDebt'].iloc[0].item())
        last_terminal_value = float(self.dcf['Unlevered_CashFlow'].iloc[-1].item())

        terminal_value = last_terminal_value * (1+self.terminal_rate) / (self.wacc - self.terminal_rate)
        present_terminal_value = terminal_value / ((1 + self.wacc) ** self.period)
        enterprise_value = sum(self.dcf['Present_CashFlow'].iloc[self.period:]) + present_terminal_value
        equity = enterprise_value - net_debt
        return float(equity / self.get_shares_outstanding())

    def prepare_data_for_dcf(self) -> pd.DataFrame:
        """
        Prepares and aligns the income statement, cash flow statement, and balance sheet data
        necessary for DCF analysis.

        Returns:
            pd.DataFrame: DCF-ready DataFrame containing:
                - revenue
                - ebit
                - nopat
                - da (depreciation & amortization)
                - capex
                - nwc (net working capital)
        """
        self.adjust_index_time()
        date_index = [pd.to_datetime(year) for year in self.income_sheet.index]
        future_index = [date_index[0] + pd.DateOffset(years=i) for i in range(1, self.period + 1)]
        index = sorted((date_index + future_index[::-1]))

        data = {
            'revenue': self.income_sheet['revenue'].reindex(index),
            'ebit': (self.income_sheet['ebitda'] - self.cash_sheet['DA']).reindex(index),
            'nopat': ((self.income_sheet['ebitda'] - self.cash_sheet['DA']) * (1 - self.tax_rate)).reindex(index),
            'da': self.cash_sheet['DA'].reindex(index),
            'capex': self.cash_sheet['capEx'].reindex(index),
            'nwc': self.balance_sheet['netWorkingCapital'].reindex(index),
        }
        return pd.DataFrame(data, index=index)

    def calculate_share_price(self):
        """
        Executes the full DCF workflow:
            1. Forecast financial statement categories.
            2. Compute future free cash flows.
            3. Apply valuation method (perpetuity or exit multiple).
            4. Optionally export to Excel.

        Returns:
            None
        """
        self.forcast_categories()
        self.get_future_fcf()
        func_name = f'{self.method}_method'
        assert hasattr(self, func_name), f'[ERROR] Unknown Method stype {func_name}'
        func = getattr(self, func_name)
        self.price = func()
        if self.export:
            self.export_to_excel()

    def export_to_excel(self):
        """
        Exports the DCF model and summary to an Excel file with formatted tables and headers.

        Output:
            ExcelSheet\\DCF_Model_With_Summary.xlsx

        The export includes:
            - DCF summary (WACC, terminal growth, projection years, price, upside)
            - Detailed DCF data (historical + forecasted values)
            - Conditional formatting and table headers for readability

        Returns:
            None
        """
        dcf_summary = {
            "WACC": self.wacc,
            "Terminal Growth": self.terminal_rate,
            "Projection Years": self.period,
            "Projected Price": f'{self.price:.2f}',
            "Upside (Downside)": f'{((self.price - self.yf_info["currentPrice"]) / self.yf_info["currentPrice"]):.2f}'
        }

        if os.path.exists('ExcelSheet\\DCF_Model_With_Summary.xlsx'):
            os.remove('ExcelSheet\\DCF_Model_With_Summary.xlsx')

        with pd.ExcelWriter("ExcelSheet\\DCF_Model_With_Summary.xlsx", engine="xlsxwriter") as writer:
            startrow = 10

            self.dcf.index.name = "Date"
            self.dcf.to_excel(writer, sheet_name="DCF", index=True, startrow=startrow)

            wb = writer.book
            ws = writer.sheets["DCF"]

            # Format date columns
            date_fmt = wb.add_format({"num_format": "mmm dd yyyy", "align": "center"})
            ws.set_column("A:A", 15, date_fmt)

            for row_num, date_val in enumerate(self.dcf.index, start=startrow + 1):
                if pd.notna(date_val):
                    try:
                        ws.write_datetime(row_num, 0, pd.to_datetime(date_val).to_pydatetime(), date_fmt)
                    except Exception:
                        ws.write(row_num, 0, str(date_val), date_fmt)

            # Format headers and summary
            title_fmt = wb.add_format({
                "bold": True, "font_size": 14, "align": "center", "valign": "vcenter"
            })
            ws.merge_range("A1:I1", f"Discounted Cash Flow (DCF) Model ({self.method} method)", title_fmt)

            header_fmt = wb.add_format({
                "bold": True, "bg_color": "#DCE6F1", "border": 1, "align": "left"
            })
            label_fmt = wb.add_format({"align": "left", "border": 1})
            value_fmt = wb.add_format({"num_format": "0.0%", "align": "right", "border": 1})

            # Write summary section
            ws.write("A3", "DCF Summary", header_fmt)
            ws.write("A4", "WACC", label_fmt)
            ws.write("A5", "Terminal Growth", label_fmt)
            ws.write("A6", "Projection Years", label_fmt)
            ws.write("A7", "Projected Price", value_fmt)
            ws.write("A8", "Upside (Downside)", label_fmt)

            ws.write("B4", dcf_summary["WACC"], value_fmt)
            ws.write("B5", dcf_summary["Terminal Growth"], value_fmt)
            ws.write("B6", dcf_summary["Projection Years"], wb.add_format({"align": "right", "border": 1}))
            ws.write("B7", dcf_summary["Projected Price"], wb.add_format({"align": "right", "border": 1}))
            ws.write("B8", dcf_summary["Upside (Downside)"], value_fmt)

            # Format data table columns
            header_fmt_table = wb.add_format({
                "bold": True, "bg_color": "#DCE6F1", "border": 1,
