from typing import Union

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette import status

from src.shared.generics import ValidationError, ErrorResponse
from src.utils.constants import ErrorsIDs, ErrorsDescriptions


class BaseHttpException(Exception):
    pass


class HttpException(BaseHttpException):
    status_code: int
    error_id: int
    description: str
    headers: Union[dict, None] = None

    def __init__(self, status_code, error_id, description, headers: Union[dict, None] = None):
        super().__init__()
        self.status_code = status_code
        self.description = description
        self.error_id = error_id
        self.headers = headers


class AuthException(BaseHttpException):
    error_id: int
    description: str

    def __init__(self, error_id, description):
        self.error_id = error_id
        self.description = description


def http_response_exception_handler(_: Request, ex: HttpException):
    return JSONResponse(
        status_code=ex.status_code,
        headers=ex.headers,
        content=dict(
            error=ErrorResponse(errorId=ex.error_id, description=ex.description).to_json()
        )
    )


def internal_server_exception_handler(_: Request, __: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=dict(
            error=ErrorResponse(
                errorId=ErrorsIDs.INTERNAL_SERVER_ERROR,
                description=ErrorsDescriptions.INTERNAL_SERVER_ERROR
            ).to_json()
        )
    )


def request_validation_error_exception_handler(_: Request, ex: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=dict(
            error=ValidationError(
                errorId=ErrorsIDs.VALIDATION_ERROR,
                description=ErrorsDescriptions.VALIDATION_ERROR,
                details=jsonable_encoder({"errors": ex.errors(), "body": ex.body})
            ).to_json()
        )
    )


def auth_exception_handler(_: Request, ex: AuthException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=dict(
            error=ErrorResponse(errorId=ex.error_id, description=ex.description).to_json()
        )
    )
