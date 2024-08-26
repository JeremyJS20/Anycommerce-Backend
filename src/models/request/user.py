import datetime
from typing import List, Optional, Union

from pydantic import Field, field_validator, BaseModel

from src.models.product import ProductModel, AttributeType
from src.shared.generics import CommonModel
from src.utils.constants import PaymentMethodType


class CartInfoModel(CommonModel):
    amount: int = Field(ge=1)
    variants: Optional[List[AttributeType]] = None


class CartModelRequest(CommonModel):
    product: ProductModel
    cartInfo: CartInfoModel


class CartRequest(CommonModel):
    userId: Optional[str] = None
    cart: List[CartModelRequest]


class PaymentMethodTypeCardBasicModel(CommonModel):
    stripeId: Optional[str] = Field(min_length=1, default=None)
    company: Optional[str] = Field(min_length=1, default=None)
    name: Optional[str] = Field(min_length=1, max_length=50, default=None)
    ending: Optional[str] = Field(min_length=1, max_length=4, examples=['0000'], default=None)
    expirationDate: Optional[str] = Field(min_length=1, max_length=7, examples=['MM/YYYY'], default=None)


class PaymentMethodTypeServiceModel(CommonModel):
    name: str


class PaymentMethodTypeServiceBasicModel(CommonModel):
    name: str


class PaymentMethodCardRequest(CommonModel):
    userId: Optional[str] = None
    type: str = Field(default=PaymentMethodType.CARD.value.lower())
    default: bool
    methodInfo: PaymentMethodTypeCardBasicModel

    @field_validator('type')
    def validate_type(cls, value: str):
        if value.lower() != PaymentMethodType.CARD.value.lower():
            raise ValueError("Payment method type not valid")
        return value


class PaymentMethodDBSchema(CommonModel):
    userId: Optional[str] = None
    type: str
    default: bool
    methodInfo: Union[PaymentMethodTypeCardBasicModel, PaymentMethodTypeServiceBasicModel]


class StripePaymentMethodCardModel(CommonModel):
    number: str
    exp_month: int
    exp_year: int
    cvc: str


class StripePaymentMethodCardRequest(CommonModel):
    customer: Optional[str] = None
    type: str = PaymentMethodType.CARD.value.lower()
    card: StripePaymentMethodCardModel
