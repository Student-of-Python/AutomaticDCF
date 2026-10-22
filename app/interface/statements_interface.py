'''
app/infrastructure/api/statements_interface.py
'''
from app.domain.enums import IncomeStatementCols, CashStatementCols, BalanceSheetCols, ErrorCode
from app.domain.entities import FinancialStatements, Result, Error, InvalidDataTypeError
from abc import ABC, abstractmethod
from pandas import DataFrame

from typing import Any

class StatementAdapter(ABC):
    '''
        Acquires financial statements
    '''


    @abstractmethod
    def _get_income(self) -> Any:
        '''
            Gets income statement
        '''
        ...

    @abstractmethod
    def _get_cash(self) -> Any:
        '''
            Returns cash statement
        '''
        ...

    @abstractmethod
    def _get_balance(self) -> Any:
        '''

            Returns balance sheet

        '''
        ...

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


    def get_statements(self) -> Result[FinancialStatements]:
        '''
        :return:
        '''


        try:
            balance = self._convert(self._get_balance(), self._balance_mapping)
            self._validate(balance, BalanceSheetCols.values_as_tuple())

            cash = self._convert(self._get_cash(), self._cash_mapping)
            self._validate(cash, CashStatementCols.values_as_tuple())

            income = self._convert(self._get_income(), self._income_mapping)
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