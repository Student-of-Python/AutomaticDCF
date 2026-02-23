""""
Responsiblity: Process macro trend data accordingly
Assuming from MACROTRENDS.COM

"""""
from request_fundamentals import StatementType
from process_http import ProcessHTTPRequests
import pandas as pd
from dataclasses import dataclass
from requests import Response

@dataclass
class ProcessMacroFundamentalsConfigs:
    pass


class ProcessMacroFundamentals:
    def process_data(self, data: Response, statement_type: StatementType):

        if statement_type.name == StatementType.income_statement:
            return self._process_income_stmt(data)
        return

    def _process_income_stmt(self, data: Response) -> pd.DataFrame:
            data = ProcessHTTPRequests.parse_table()
