from rapidfuzz import process
import requests
import pandas as pd
from openbb import obb
import re
from googlesearch import search
from bs4 import BeautifulSoup
from selenium import webdriver
import difflib
import time
import os




def extract_website(file_name, url, refresh = False): #--> Calls extract website with following params
    def decorator(func): #Gets the function that will be decorated
        def wrapper(self, *args, **kwargs): #--> Makes file before function is called.
            if refresh or not os.path.exists(file_name):
                driver = webdriver.Chrome()
                driver.get(url)
                time.sleep(3)
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(driver.page_source)
                driver.quit()
            return func(self, *args, **kwargs) #Used self because of class
        return wrapper
    return decorator

class Fundemental_Data():
    def __init__(self, ticker, period, provider = 'yfinance', API_KEY = None):
        self.ticker = ticker
        self.provider = provider.lower()
        self.period = period
        self.balance_sheet, self.cash_sheet, self.income_sheet, self.general_info = self.get_fundamental_statements()

        #API KEYS
        self.fmp_api_key =   'mKlC3RuSSiBVpsNmTAdBtGHp1pZ9oYan' #'0gIMVqR7FC7oya8LtUKnpRe5FwhJZ8ZS'
        self.base_url = 'https://financialmodelingprep.com/api/'
        #General
        self.country_mapping = self.mk_country_mapping()

    def get_fundamental_statements(self):
        '''

        Returns: Fundemental Data and General Info

        '''
        #https://finviz.com/quote.ashx?t=AAPL&p=d is a good substitute

        try:
            balance_sheet = obb.equity.fundamental.balance(self.ticker, provider = self.provider, limit = self.period).to_df()
            cash_sheet = obb.equity.fundamental.cash(self.ticker, provider = self.provider, limit = self.period).to_df()
            income_sheet = obb.equity.fundamental.income(self.ticker, provider = self.provider, limit = self.period).to_df()
            general_info = obb.equity.profile(self.ticker, self.provider).to_df()
        except Exception as error:
            print(f'Error in Fundamental Statement extraction using {self.provider}:\n'
                  f'Defaulting to yfinance data, 3 years')
            self.provider = 'yfinance'
            return self.get_fundamental_statements()
        return balance_sheet, cash_sheet, income_sheet, general_info

    def get_cost_of_equity(self):
        ''''
        Cost of equity = Rf + B(Rm - Rf)
        (Rm - Rf) --> total equity risk premium
        '''
        #Country mapping

        risk_free = self.get_yield_rate() / 100
        beta = self.get_similar_columns(self.general_info, ['beta'], latest = True).item()

        country_name = self.get_similar_columns(self.general_info, ['country'], latest=True).item()

        try:
            excel_sheet = pd.read_excel(r'Data/RiskFreeRates2025.xlsx', sheet_name='PRS Worksheet')
            excel_country_column = excel_sheet['Country'].dropna().astype(str).to_list()
            best_country = self.get_most_similiar_word(country_name, excel_country_column)
            equity_risk_premium = (excel_sheet.loc[excel_sheet['Country'] ==  best_country, 'Final ERP'].iloc[0])
            #Going to get something like 4.33%, want to get 4.33 as float (already in %)
        except KeyError:
            raise ValueError(f"Could not parse ERP for {country_name}")
        return risk_free + beta * equity_risk_premium

    def get_cost_of_debt(self):
        '''

        Cost of debt =
            (interest expense / total debt) * (1 - tax rate)

        tax rate =
            Income tax expense  / EBT
            tax rate is not in %

        Returns: cost of debt
        '''


        self.interest_expense = self.get_similar_columns(self.income_sheet, ['interest expense'], latest=True).item()
        self.income_tax_expense = self.get_similar_columns(self.income_sheet, ['tax expense'],latest=True).item()
        self.income_before_tax = self.get_similar_columns(self.income_sheet, ['income before tax'],latest=True).item()
        self.total_debt = self.get_similar_columns(self.balance_sheet, ['total debt'],latest=True).item()
        self.total_equity = self.get_similar_columns(self.balance_sheet, ['total equity'],latest=True).item()
        self.tax_rate = (self.income_tax_expense / self.income_before_tax)

        return (self.interest_expense / self.total_debt)

    def calculate_WACC(self):
        '''
        WACC = (Cd) * (D / (D+E)) + (Ce)*(E / (E+D)) * (1-T)
        where Cd --> cost of debt
              Ce --> Cost of equity
              D --> total debt
              E --> total equity
              T -- > Tax Rate
        Returns: WACC

        '''
        cost_of_debt = self.get_cost_of_debt()
        cost_of_equity =  self.get_cost_of_equity()
        return (cost_of_debt) * (self.total_debt / (self.total_debt + self.total_equity)) + (cost_of_equity) * (self.total_equity / (self.total_debt + self.total_equity))

    def get_most_similiar_word(self, keyword, list_):
        word, score, index = process.extractOne(keyword, list_)
        return word

    def get_similar_columns(self, df:pd.DataFrame, columns:list, latest = False):
        df_columns = df.columns
        similiar_columns = [self.get_most_similiar_word(column_name, df_columns) for column_name in columns]
        return df[similiar_columns] if not latest else df[similiar_columns].iloc[0]

    @extract_website('Archive/Data/country_codes', 'https://www.iban.com/country-codes', refresh = False)
    def mk_country_mapping(self):
        ''''
        Mapping of all the countries codes.
        i.e
        US --> United States
        '''
        with open('Archive/Data/country_codes', 'r', encoding='utf-8') as file:
            contents = file.read()

        table = pd.read_html(contents)[0]
        return dict(zip(table.iloc[: , 1], table.iloc[: , 0]))

    @extract_website('Archive/Data/bond_yield_html', 'https://tradingeconomics.com/bonds', refresh=False)
    def get_yield_rate(self):
        ''''
        Gets yield rate by scraping tradingecon website.

        '''
        #Read from file with page source
        with open('Archive/Data/bond_yield_html', 'r', encoding='utf-8') as file:
            contents = file.read()

        #Pandas HTML
        tables = pd.read_html(contents)

        #   Links mapping together

        #combining tables
        dfs = [df.set_axis(range(df.shape[1]), axis=1) for df in tables]
        combined_df = pd.concat(dfs, ignore_index=True)

        #Uses best ratio to find countr
        country_name = self.get_similar_columns(self.general_info,['country'], latest = True).item()
        country_name = self.get_most_similiar_word(country_name, combined_df.iloc[:, 1].to_list())
        combined_df = combined_df.set_index(1)

        yield_value = combined_df.loc[country_name,2]

        return yield_value

    def search_(self, search_phrase, keyword,  amount = 5, regex_format= r'\b\d+\.?\d+?[%]', auto = False):
        '''

        Args:
            search_phrase: Search input into google
            keyword: Narrow down the search; what you are looking for
            amount: number of links to search

        Returns: returns the most probable text decided by user

        '''
        results = []
        possible_matches = []
        search_results = list(search(search_phrase, num_results= amount))
        for number, link in enumerate(search_results):
            try:
                decorated_func = extract_website(f'Website_Searches/Search{number}', link, refresh=True)(self.scrape_keyword)
                possible_phrases_detected = decorated_func(keyword, f'Website_Searches/Search{number}')
                results.append(possible_phrases_detected)
            except KeyError:
                print(f'{KeyError} on {link}. Skipping')
                pass

        if auto:
            results = results[0]
            possible_matches = [re.findall(rf'{regex_format}', sub_string, flags=re.IGNORECASE) for sub_string in
                                results]
            print(f'Returning {possible_matches[0]}')
            return possible_matches[0][0]

        for some_result in results:
            print(some_result)
            answer = input('Press 1 to accept, 0 to deny\n')
            if answer == '0':
                pass
            elif answer == '1':
                possible_matches = [re.findall(rf'{regex_format}', sub_string, flags=re.IGNORECASE) for sub_string in
                                    some_result]
                break
        if possible_matches:
            for value in possible_matches:
                print(value)
                answer = input('Return this value? Press 1 to accept, 0 to deny\n')
                if answer == '0':
                    pass
                elif answer == '1':
                    return value[0]

        else:
            return None


    def get_attribute(self, name):
        return getattr(self,name) if hasattr(self,name) else None


    def scrape_keyword(self, keyword, filename, regex_format= r'\b\d+\.?\d+?[%]'):
        '''

        Args:
            keyword: What to look for
            filename: Filename

        Returns: a possible match

        '''
        with open(filename, 'r', encoding='utf-8') as file:
            contents = file.read()

        soup = BeautifulSoup(contents, 'html.parser')
        #Getting rid of unnessasary styles
        for element in soup(['script', 'style', 'meta', 'noscript', 'iframe']):
            element.decompose()

        #Getting all text, further clean up
        text = soup.get_text(separator= ' ', strip=True)

        possible_phrase_match = re.findall(rf'[^.?!]*\b{re.escape(keyword)}\b[^.?!]*{regex_format}', text, flags = re.IGNORECASE)

        #possible_matches = [re.findall(rf'{regex_format}', sub_string, flags = re.IGNORECASE) for sub_string in possible_phrase_match]

        return possible_phrase_match

    def convert_percent_to_float(self, string: str) -> float:
        #Can use l or r strip next time?
        return float(re.findall(r'\d+\.?\d+?', string)[0]) / 100






