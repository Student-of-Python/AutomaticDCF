from typing import Optional, List
from bs4 import BeautifulSoup
from requests import Response
import pandas as pd
import re
import json




class ProcessHTTPRequests:


    def parse_table(self, res: Response) -> Optional[List[pd.DataFrame]]:
        """
        :param res: http response
        :return: table, if found
        """
        self._valid_response(res)
        tables = pd.read_html(res.content)
        return tables

    def parse_content(self, res: Response) -> Optional[str]:
        """
        :param res:
        :return: contents of the site (pdf, images, audio)
        """

        self._valid_response(res)
        content = res.content
        return content

    def parse_text(self, res: Response) -> Optional[str]:
        """
        :param res:
        :return: text of website
        """
        self._valid_response(res)
        text = res.text
        return text

    @staticmethod
    def parse_json_from_text(text: str) -> Optional[dict]:
        """
        :param text:
        :return:
        """

        soup = BeautifulSoup(text, 'html.parser')
        script_tags = soup.find_all('script')

        for script in script_tags:
            if script.string and 'originalData' in script.string:
                match = re.search(r"var originalData = (\[.*?\]);", script.string, re.DOTALL)
                if match:
                    return json.loads(match.group(1))

        raise ValueError("Could not find originalData JSON in page")

    @staticmethod
    def parse_dataframe_from_json(json_: dict) -> Optional[pd.DataFrame]:
        """
        :param json_:
        :return:
        """
        records = []
        for entry in json_:
            raw_field = entry.get('field_name', '')
            clean_field = BeautifulSoup(raw_field, "html.parser").get_text(strip=True)

            row = {k: v for k, v in entry.items() if k not in ["field_name", "popup_icon"]}
            row["field_name"] = clean_field
            records.append(row)

        df = pd.DataFrame(records).set_index("field_name").T
        df = df.apply(pd.to_numeric, errors="coerce")
        df.dropna(how='all', axis=1, inplace=True)
        return df

    @staticmethod
    def _valid_response(res: Response) -> None:
        """
        :param res: Response
        :return: if valid response
        """

        if not isinstance(res, Response):
            raise ValueError("[ERROR] Given object is not response")

        if not Response.ok:
            raise ValueError("[ERROR] Not a valid response")



