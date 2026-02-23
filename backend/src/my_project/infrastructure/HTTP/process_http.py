from typing import Optional, List
from bs4 import BeautifulSoup
from requests import Response
import pandas as pd
import re
import json

"""
ProcessHTTPRequests

Collection of helping functions
"""


class ProcessHTTPRequests:
    @staticmethod
    def parse_table(res: Response) -> Optional[List[pd.DataFrame]]:
        """
        :param res: http response
        :return: table, if found
        """
        ProcessHTTPRequests._valid_response(res)
        tables = pd.read_html(res.content)
        return tables

    @staticmethod
    def parse_content(res: Response) -> Optional[str]:
        """
        :param res:
        :return: contents of the site (pdf, images, audio)
        """

        ProcessHTTPRequests._valid_response(res)
        content = res.content
        return content

    @staticmethod
    def parse_text(res: Response) -> Optional[str]:
        """
        :param res:
        :return: text of website
        """
        ProcessHTTPRequests._valid_response(res)
        text = res.text
        return text

    @staticmethod
    def parse_json(res: Response) -> Optional[str]:
        """
        :param res:
        :return:
        """
        ProcessHTTPRequests._valid_response(res)
        js = res.json()
        return js

    @staticmethod
    def parse_dataframe_from_text(text: str) -> Optional[pd.DataFrame]:
        json_ = ProcessHTTPRequests.parse_json_from_text(text)
        data = ProcessHTTPRequests.parse_dataframe_from_json(json_)
        return data

    @staticmethod
    def parse_dataframe_from_response(res: Response) -> Optional[pd.DataFrame]:
        ProcessHTTPRequests._valid_response(res)
        #TODO: Handle Error exceptions. Do I even need this?
        data = ProcessHTTPRequests.parse_dataframe_from_text(res.content)
        return data



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

        if not res.ok:
            raise ValueError("[ERROR] Not a valid response")



