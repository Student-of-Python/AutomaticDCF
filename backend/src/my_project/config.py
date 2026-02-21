from typing import Union, Optional
from dataclasses import dataclass


@dataclass
class RequestFundamentalsConfig:
    ticker: str
