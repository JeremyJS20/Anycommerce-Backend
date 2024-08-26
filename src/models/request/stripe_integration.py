from pydantic import Field

from src.shared.generics import CommonModel


class CalculateTaxesRequest(CommonModel):
    addressId: str = Field(min_length=1, max_length=50)
