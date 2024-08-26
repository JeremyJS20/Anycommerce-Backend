from typing import Optional, TypeVar, Generic

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.utils.utils import camel_to_snake_case

T = TypeVar('T')
T2 = TypeVar('T2')


class CommonModel(BaseModel):
    def to_json(self):
        return self.model_dump(mode='json')

    def to_schema(self) -> dict:
        return camel_to_snake_case(self.model_dump())


class CommonResponseModel(BaseModel):
    def to_json(self):
        return self.model_dump(mode='json')


class Data(CommonModel, Generic[T]):
    data: T


class DataWithAdditional(CommonModel, Generic[T, T2]):
    data: T
    additionalData: Optional[T2] = None


class PaginationData(CommonModel):
    currentPage: int
    totalPageRecords: int
    totalRecords: int
    totalPages: int


class MessageResponse(CommonModel):
    message: str


class MessageWithStatusResponse(CommonModel):
    status: str
    message: str


class ErrorResponse(CommonModel):
    errorId: int
    description: str


class ValidationError(CommonModel):
    errorId: int
    description: str
    details: dict


class Error(CommonModel, Generic[T]):
    error: T
