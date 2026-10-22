'''
app/domain/exceptions.py
'''
from dataclasses import dataclass
from typing import Optional, Any
from enum import StrEnum

class ErrorCode(StrEnum):
    FAILED_REQUEST = "FAILED_REQUEST"
    INVALID_DATA = 'INVALID_DATA'
    KEY_ERROR = 'KEY_ERROR'
    UNKNOWN_ERROR = 'UNKNOWN_ERROR'

@dataclass(frozen=True)
class Error:
    code: ErrorCode
    msg: str
    details: Optional[dict[str, Any]] = None

    @classmethod
    def failed_request(cls, request_msg: str, params: dict) -> Error:
        return cls(code = ErrorCode.FAILED_REQUEST, msg = request_msg, details = params)

    @classmethod
    def invalid_data(cls, msg: str, details: dict) -> Error:
        return cls(code = ErrorCode.INVALID_DATA, msg = msg, details = details)

    def __repr__(self) -> str:
        return (f'ERROR: {self.code} '
                f'MSG: {self.msg} '
                f'DETAILS: {self.details}')

class InvalidDataTypeError(Exception):
    pass