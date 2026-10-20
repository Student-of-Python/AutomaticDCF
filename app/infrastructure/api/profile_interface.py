'''
app/infrastructure/api/profile_interface.py
'''
from app.domain.entities import Result, CompanyProfile
from abc import ABC, abstractmethod

class ProfileAdapter(ABC):
    ''''''

    @abstractmethod
    def _get_country(self):
        ...

    @abstractmethod
    def _get_beta(self):
        ...

    @abstractmethod
    def _get_shares_outstanding(self):
        ...

    @abstractmethod
    def _get_current_price(self):
        ...

    @abstractmethod
    def _get_ev_ebitda_multiple(self):
        ...

    #Need conversion, validation???


    def get_profile(self) -> Result[CompanyProfile]:
        ''''''

        try:
            country = self._get_country()
            beta = self._get_beta()
            shares_outstanding = self._get_shares_outstanding()
            current_price = self._get_current_price()
            ev_ebitda_multiple = self._get_ev_ebitda_multiple()

        except Exception as err:
            ...


        return Result.success(result = CompanyProfile(
            country = country,
            beta = beta,
            shares_outstanding = shares_outstanding,
            current_price = current_price,
            ev_ebitda_multiple = ev_ebitda_multiple
        ))