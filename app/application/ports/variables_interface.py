'''
app/ports/variables_interface.py
'''
from app.domain.entities import MacroVariables, Result
from app.domain.exceptions import Error, ErrorCode
from abc import ABC, abstractmethod
from typing import TypeAlias, Protocol

RiskFree: TypeAlias = float
EquityPremium: TypeAlias = float

class EquityPremiumProvider(Protocol):
    def get_equity_premium(self, country: str) -> EquityPremium:
        '''Returns equity risk premium as a float'''
        ...

class RiskFreeProvider(Protocol):
    def get_risk_free(self, country: str) -> RiskFree:
        '''Returns the risk free rate as a float'''
        ...

class MacroAdapter(ABC):

    @abstractmethod
    def _fetch_data(self, country: str) -> tuple[RiskFree, EquityPremium]:
        ''''''
        pass

    def get_macro(self, country: str) -> Result[MacroVariables]:
        '''Gets Macro Variables'''
        try:
            data: tuple[RiskFree, EquityPremium] = self._fetch_data(country)

            macro_vars = MacroVariables(
                risk_free_rate = data[0],
                equity_premium_rate = data[1]
            )

        except KeyError as err:
            return Result.failed(error = Error(code = ErrorCode.KEY_ERROR, msg = str(err)))

        except (TimeoutError, ConnectionError) as err:
            return Result.failed(error = Error(
                code = ErrorCode.FAILED_REQUEST,
                msg = 'Failed Data Request',
                details = {'Error message' : err}
            ))

        except Exception as err:
            return Result.failed(error= Error(code = ErrorCode.UNKNOWN_ERROR, msg = str(err)))


        return Result.success(result = macro_vars)


