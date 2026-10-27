'''
app/infrastructure/api/profile_interface.py
TODO: Add tests
'''
from app.domain.exceptions import ErrorCode, Error, InvalidDataTypeError
from app.domain.entities import Result, CompanyProfile
from abc import ABC, abstractmethod
from typing import Any


class ProfileAdapter(ABC):
    ''''''

    @abstractmethod
    def _fetch_profile_data(self, ticker:str) -> Any:
        ...

    @staticmethod
    def _validate(data: dict[str, Any]) -> None:
        '''Validates if data is correct'''

        _key = {'country', 'beta', 'shares_outstanding', 'current_price', 'ev_ebitda_multiple'}

        _are_missing = len(_key - set(data.keys())) > 0

        #For now, we just check existance, perhaps later on value check?
        #TODO: Make a specific exception for this
        if _are_missing:
            raise InvalidDataTypeError(f"Expected key mismatch. Redundant keys: {set(data.keys()) - _key}")

    def get_profile(self, ticker: str) -> Result[CompanyProfile]:
        ''''''

        try:
            data = self._fetch_profile_data(ticker = ticker)
            self._validate(data)
            profile = CompanyProfile.from_dict(data)

        except (ConnectionError, TimeoutError) as err:
            return Result.failed(error = Error(
                code = ErrorCode.FAILED_REQUEST,
                msg = 'Failed Data Request',
                details = {'Error message' : err}
            ))

        except InvalidDataTypeError as err:

            return Result.failed(error=Error.invalid_data(

                msg='Key Error Exception Occurred During Conversion',

                details={'Error message': err}

            ))

        except Exception as err:

            return Result.failed(error=Error(

                code=ErrorCode.UNKNOWN_ERROR,

                msg='Unknown Error Occurred!',

                details={'Error message': err}

            ))

        return Result.success(result = profile)

'''
Need to finish validation
Restructure interface 
Reimplement Yfinance profile 

-> Design in such a way that is it resilent. 
'''