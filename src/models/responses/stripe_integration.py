from datetime import datetime
from typing import Union

from pydantic import Field

from src.shared.generics import CommonModel
from src.utils.constants import PaymentIntentStatus


class SetupIntentResponse(CommonModel):
    setupIntentId: str
    paymentIntentId: str
    clientSecret: str
    userId: str
    status: str
    initiationDate: datetime
    endDate: Union[None, datetime]


class PaymentMethodResponse(CommonModel):
    id: str
    brand: str
    ending: str
    expirationDate: str
    default: bool
    type: str


class CalculateTaxesResponse(CommonModel):
    total: int
    inclusiveTaxes: int
    exclusiveTaxes: int


class OrderContactInfoModel(CommonModel):
    email: str = Field(min_length=1)
    phone: str = Field(min_length=1)


class PlaceOrderRequest(CommonModel):
    contactInfo: OrderContactInfoModel
    shippingAddress: str = Field(min_length=1)
    paymentMethod: str = Field(min_length=1)
