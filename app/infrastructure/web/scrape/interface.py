'''
app/infrastructure/web/interface.py
======================================
'''
from abc import ABC, abstractmethod


class Scraper(ABC):


    @abstractmethod
    def scrape(self) -> None:
        ...