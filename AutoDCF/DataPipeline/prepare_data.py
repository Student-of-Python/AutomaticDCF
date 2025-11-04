from AutoDCF.DataPipeline.fundamental_collector import ExtractFundamentals
from typing import Union, Optional, Literal
from AutoDCF.DataPipeline.searchonline import search
from AutoDCF.DataPipeline.api_clients import *
from AutoDCF.DataPipeline.helper import *


class PrepareData:
    """
    The PrepareData class orchestrates the retrieval and preprocessing of financial data
    necessary for DCF (Discounted Cash Flow) modeling.

    It collects fundamentals, financial ratios, and macroeconomic data across APIs and
    stored data sources, while providing helper methods for cost and valuation calculations.

    The class can operate in both automatic and manually overridden modes via decorators.

    Attributes:
        ticker (str): Target stock ticker (standardized to uppercase).
        period (int): Number of years of financial data to retrieve.
        manual_input (dict): Optional manual data overrides for critical values.
        fundamental_data (ExtractFundamentals): Object managing macrotrend data extraction.
        yf_info (dict): Yahoo Finance API data for the ticker.
        fmp_info (pd.DataFrame): Financial Modeling Prep profile data.
        balance_sheet (pd.DataFrame): Historical balance sheet.
        income_sheet (pd.DataFrame): Historical income statement.
        cash_sheet (pd.DataFrame): Historical cash flow statement.
        country_alpha (str): Two-letter ISO country code.
        country_name (str): Full country name.
        income_tax_expense (float): Latest income tax expense.
        interest_expense (float): Latest interest expense.
        total_debt (float): Latest total debt figure.
        total_equity (float): Latest total equity figure.
        ebt (float): Latest earnings before tax.
        beta (float): Beta coefficient (systematic risk factor).
        tax_rate (float): Effective tax rate.
        yield_rate (float): Country-level yield rate (proxy for risk-free rate).
        industry (str): Company’s primary industry classification.
    """

    @manual_init
    def __init__(self, ticker: str, period: int = 4, **kwargs):
        """
        Initializes the PrepareData object and retrieves all key financial and market data.

        Args:
            ticker (str): Ticker symbol for the target company.
            period (int): Number of past years to retrieve (default = 4).
            **kwargs: Optional keyword arguments (e.g., 'manual_input' overrides).
        """
        # Manual input overrides for key values (used in modeling adjustments)
        self.manual_input = kwargs.get('manual_input')

        # Initialize ticker and period attributes
        self.ticker = ticker.upper()
        self.period = period

        # Retrieve fundamental data from Macrotrends via ExtractFundamentals
        self.fundamental_data = ExtractFundamentals(ticker=self.ticker, years_back=self.period)

        # Initialize API clients
        self.yf_info = get_yf_info(self.ticker)
        self.fmp_info = get_fmp_profile(self.ticker)

        # Extract major financial statements
        self.balance_sheet = self.fundamental_data.get_macrotrend_data('balance')
        self.income_sheet = self.fundamental_data.get_macrotrend_data('income')
        self.cash_sheet = self.fundamental_data.get_macrotrend_data('cash')

        # Derive geographic identifiers
        self.country_alpha = self.fmp_info[get_keyword(self.fmp_info.columns, 'country')].item()
        self.country_name = get_country_from_alpha(self.country_alpha)

        # Core financial variables (with manual override support)
        self.income_tax_expense = self.manual_input.get(
            'income_tax_expense', get_latest(self.income_sheet, 'incomeTaxExpense')
        )
        self.interest_expense = self.manual_input.get(
            'interest_expense', get_latest(self.income_sheet, 'interestExpense')
        )
        self.total_debt = self.manual_input.get(
            'total_debt', get_latest(self.balance_sheet, 'totalDebt')
        )
        self.total_equity = self.manual_input.get(
            'total_equity', get_latest(self.balance_sheet, 'totalEquity')
        )
        self.ebt = self.manual_input.get('ebt', get_latest(self.income_sheet, 'ebt'))
        self.beta = self.manual_input.get(
            'beta', self.fmp_info[get_keyword(self.fmp_info.columns, 'beta')].item()
        )

        # Derived ratios
        self.tax_rate = self.manual_input.get('tax_rate', float(self.income_tax_expense / self.ebt))
        self.yield_rate = self.manual_input.get('yield_rate', get_yield_rate(self.country_name))
        self.industry = self.manual_input.get(
            'industry', self.fmp_info[get_keyword(self.fmp_info.columns, 'industry')].item()
        )

    def get_cost_of_debt(self) -> Union[float, int]:
        """
        Computes the pre-tax cost of debt.

        Formula:
            Cost of Debt = (Interest Expense / Total Debt)

        Note:
            The tax-adjusted cost of debt is applied in the WACC formula separately.

        Returns:
            float: The cost of debt as a decimal (not percentage).
        """
        return self.interest_expense / self.total_debt

    def get_cost_of_equity(self) -> Union[float, int]:
        """
        Calculates the cost of equity using the Capital Asset Pricing Model (CAPM).

        Formula:
            Cost of Equity = Rf + β(Rm - Rf)

        where:
            Rf = risk-free rate (country yield)
            β = beta (systematic risk)
            (Rm - Rf) = market equity risk premium (ERP)

        Returns:
            float: Cost of equity (decimal form).

        Raises:
            ValueError: If ERP data cannot be parsed from the Excel sheet.
        """
        risk_free = float(self.yield_rate / 100)

        try:
            excel_sheet = pd.read_excel(
                r'C:\Users\gleb\FinProject2025\AutoDCF\DataPipeline\Data\RiskFreeRates2025.xlsx',
                sheet_name='PRS Worksheet'
            )
            excel_country_column = excel_sheet['Country'].dropna().astype(str).to_list()
            local_country_name = get_keyword(excel_country_column, self.country_name)
            equity_risk_premium = excel_sheet.loc[
                excel_sheet['Country'] == local_country_name, 'Final ERP'
            ].item()
        except KeyError:
            raise ValueError(f"Could not parse ERP for {self.country_name}")

        return risk_free + self.beta * equity_risk_premium

    @manual_override('WACC')
    def calculate_wacc(self) -> Union[float, int]:
        """
        Computes the Weighted Average Cost of Capital (WACC).

        Formula:
            WACC = (Ce * (E / (E + D))) + (Cd * (D / (E + D)) * (1 - T))

        where:
            Ce = Cost of equity
            Cd = Cost of debt
            E = Total equity
            D = Total debt
            T = Tax rate

        Returns:
            float: Weighted average cost of capital (decimal form).
        """
        cost_of_debt = self.get_cost_of_debt()
        cost_of_equity = self.get_cost_of_equity()

        return cost_of_equity * (self.total_equity / (self.total_equity + self.total_debt)) + \
            cost_of_debt * (self.total_debt / (self.total_equity + self.total_debt)) * (1 - self.tax_rate)

    @manual_override('Terminal_Growth_Rate')
    def get_cagr(self, amount: int = 5, choose: bool = True) -> float:
        """
        Retrieves or estimates the compound annual growth rate (CAGR) from online sources.

        This function searches the web for the most relevant CAGR estimate associated with
        the company and industry.

        Args:
            amount (int): Number of top search results to parse (default = 5).
            choose (bool): Whether to prompt for manual selection if multiple matches.

        Returns:
            float: Extracted CAGR value as a decimal.
        """
        search_phrase = f'{self.ticker} {self.industry} CAGR GROWTH'
        return search(
            search_phrase=search_phrase,
            keyword='CAGR',
            keyword_regex=r'\\b\\d+\\.?\\d+?[%]',
            amount=amount,
            choose=choose,
            func=convert_percent_to_float
        )

    @manual_override('Shares_Outstanding')
    def get_shares_outstanding(self) -> int:
        """
        Estimates the total number of shares outstanding using Yahoo Finance data.

        Formula:
            Shares Outstanding = Market Cap / Current Price

        Returns:
            int: Approximate total shares outstanding.
        """
        return int(self.yf_info.get('marketCap') / self.yf_info.get('currentPrice'))

    @manual_override('Exit_Multiple')
    def get_ev_ebidta_multiple(
        self,
        mode: Literal['historical', 'basket'] = 'historical',
        industry: Optional[Literal['sector', 'industry', 'subIndustry']] = 'industry'
    ) -> float:
        """
        Retrieves the EV/EBITDA multiple either from historical data or a peer basket.

        Args:
            mode (Literal['historical', 'basket']): Source mode.
                - 'historical': Uses the company's own trailing EV/EBITDA.
                - 'basket': Averages multiples across industry peers.
            industry (Literal['sector', 'industry', 'subIndustry'], optional):
                Granularity for peer comparison (default = 'industry').

        Returns:
            float: EV/EBITDA multiple.
        """
        if mode == 'historical':
            return float(self.yf_info.get('enterpriseToEbitda'))

        basket = get_finnhub_peers(self.ticker, industry_type=industry)
        if not basket:
            print(f'[ERROR] Basket Mode not available (size: {len(basket)}). Defaulting to historical mode')
            return self.get_ev_ebidta_multiple(mode='historical', industry=None)

        multiples = [get_yf_info(stock).get('enterpriseToEbitda') for stock in basket]
        return float(sum(multiples) / len(multiples))

    def adjust_index_time(self):
        """
        Ensures all financial statement DataFrame indices are converted to datetime
        and synchronized across balance sheet, income statement, and cash flow data.

        Raises:
            AssertionError: If date indices between the financial statements do not match.
        """
        self.income_sheet.index = pd.to_datetime(self.income_sheet.index)
        self.cash_sheet.index = pd.to_datetime(self.cash_sheet.index)
        self.balance_sheet.index = pd.to_datetime(self.balance_sheet.index)

        assert (
            self.income_sheet.index.equals(self.cash_sheet.index)
            and self.income_sheet.index.equals(self.balance_sheet.index)
        ), f'[Error] Date index is not matching: {self.income_sheet.index, self.cash_sheet.index, self.balance_sheet.index}'
