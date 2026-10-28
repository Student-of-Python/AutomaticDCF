'''
app/infrastructure/company_data/statements_interface.py
'''
from app.domain.enums import IncomeStatementCols, CashStatementCols, BalanceSheetCols
from app.domain.entities import FinancialStatements, Result
from app.domain.exceptions import ErrorCode,InvalidDataTypeError,Error
from abc import ABC, abstractmethod
from pandas import DataFrame
from typing import TypeAlias

Income: TypeAlias = DataFrame
Balance: TypeAlias = DataFrame
Cash: TypeAlias = DataFrame

class StatementAdapter(ABC):
    '''
        Acquires financial statements
    '''

    @abstractmethod
    def _fetch_raw_statements(self, ticker: str) -> tuple[Income, Balance, Cash]:
        '''fetches financial statements as dataframe'''
        pass

    @staticmethod
    def _convert(raw_data: DataFrame, col_mapping: dict) -> DataFrame:
        '''Converts to internal mapping. Expect layout to be {old : new}'''
        raw_data =  raw_data.rename(columns = col_mapping)
        return raw_data[[n for n in col_mapping.values()]] #Keep only necessary columns.

    @staticmethod
    def _validate(data: DataFrame, req_cols: tuple[str, ...]) -> Error | None:
        '''
        Validates data (missing entries or columns for now. Validation will take place in each of the "_get_..." statements.
        '''

        if bool(
            data.isna().any().any() #Any invalid values?
            or len(set(req_cols) - set(data.columns)) != 0):
            raise  InvalidDataTypeError(Error.invalid_data(msg =
                                      f'Invalid data detected!',
                                      details = {
                                          'has_NaN' : data.isna().any().any(),
                                          'missing_columns': set(req_cols) - set(data.columns) or "None",
                                          'columns_given' : data.columns,
                                      })) #Error has __repr___


    def get_statements(self, ticker: str) -> Result[FinancialStatements]:
        '''
        :return:
        '''
        #TODO: makke ticker a stateless, not instance

        try:

            r_income, r_balance, r_cash = self._fetch_raw_statements(ticker = ticker)

            income = self._convert(r_income, self._income_mapping).dropna(how='all')
            balance = self._convert(r_balance, self._balance_mapping).dropna(how='all')
            cash = self._convert(r_cash, self._cash_mapping).dropna(how='all')

            common = income.index.intersection(balance.index).intersection(cash.index)
            if common.empty:
                raise ValueError(f"No overlapping financial statement dates found for '{ticker}'.")

            income = income.loc[common].fillna(0.0)
            balance = balance.loc[common].fillna(0.0)
            cash = cash.loc[common].fillna(0.0)

            self._validate(balance, BalanceSheetCols.values_as_tuple())
            self._validate(cash, CashStatementCols.values_as_tuple())
            self._validate(income, IncomeStatementCols.values_as_tuple())


        except (ConnectionError, TimeoutError) as err:
            return Result.failed(error = Error(
                code = ErrorCode.FAILED_REQUEST,
                msg = 'Failed Data Request',
                details = {'Error message' : err}
            ))

        except InvalidDataTypeError as err:
            return Result.failed(err.args[0])

        except KeyError as err:
            return Result.failed(error = Error(
                code = ErrorCode.KEY_ERROR,
                msg = 'Key Error Exception Occured During Conversion',
                details = {'Error message' : err}
            ))

        except Exception as err:
            return Result.failed(error = Error(
                code = ErrorCode.UNKNOWN_ERROR,
                msg = 'Unknown Error Occured!',
                details = {'Error message' : err}
            ))

        return Result.success(result =
                              FinancialStatements(
                                  balance= balance,
                                  cash= cash,
                                  income = income
                              ))

    @property
    @abstractmethod
    def _income_mapping(self) -> dict[str, str]:
        ...
    @property
    @abstractmethod
    def _cash_mapping(self) -> dict[str, str]:
        ...
    @property
    @abstractmethod
    def _balance_mapping(self) -> dict[str, str]:
        ...