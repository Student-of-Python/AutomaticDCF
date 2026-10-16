'''
app/infrastructure/web/interface.py
======================================
'''
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import pandas as pd
import json


class Scraper(ABC):

    # @staticmethod
    # def _json_from_html(html: str) -> json:
    #     '''
    #     :param html:
    #     :return:
    #     '''
    #
    #     soup = BeautifulSoup(html, 'html.parser')
    #     script_tags = ...
    @abstractmethod
    def scrape(self) -> None:
        ...