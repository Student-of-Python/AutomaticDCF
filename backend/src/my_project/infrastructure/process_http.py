from requests import Response
from typing import Optional, List
import pandas as pd




class ProcessHTTPRequests:
    def parse_table(self, res: Response) -> Optional[List[pd.DataFrame]]:
        """
        :param res: http response
        :return: table, if found
        """
        self._valid_response(res)
        tables = pd.read_html(res.content)
        return tables

    def parse_string(self, res: Response) -> Optional[str]:
        """
        :param res:
        :return: contents of the site
        """

        self._valid_response(res)
        content = res.content
        return content


    def _valid_response(self, res: Response) -> None:
        """
        :param res: Response
        :return: if valid response
        """

        if not isinstance(res, Response):
            raise ValueError("[ERROR] Given object is not response")

        if not Response.ok:
            raise ValueError("[ERROR] Not a valid response")
