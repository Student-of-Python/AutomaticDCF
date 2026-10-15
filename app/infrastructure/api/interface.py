'''
app/infrastructure/api/interface.py
'''
from abc import ABC, abstractmethod
from app.domain import FinancialStatements


class StatementAdapter(ABC):
    '''
        Acquires financial statments
    '''


    @abstractmethod
    def get_income(self):
        ...

    @abstractmethod
    def get_cash(self):
        ...

    @abstractmethod
    def get_balance(self):
        ...

    @abstractmethod
    def get_statements(self) -> FinancialStatements:
        ...
