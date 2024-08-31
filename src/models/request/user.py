import datetime
import re
from typing import List, Optional, Union

from pydantic import Field, field_validator, BaseModel

from src.models.product import ProductModel, AttributeType
from src.shared.generics import CommonModel
from src.utils.constants import PaymentMethodType
from src.utils.regex import email_regex
from src.utils.utils import validate_date


class UserEmailRequest(BaseModel):
    value: str
    verified: bool

    model_config = dict(
        json_schema_extra=dict(
            example=dict(
                value="example@example.com",
                verified=False
            )
        )
    )


class UserPhoneRequest(BaseModel):
    country: str
    prefix: str
    value: str
    verified: bool

    model_config = dict(
        json_schema_extra=dict(
            example=dict(
                countryAlpha2="DO",
                prefix="+1 809",
                value="1234456",
                verified=False
            )
        )
    )


class UserRequest(CommonModel):
    stripeId: Optional[None] = None
    name: str = Field(min_length=1)
    lastName: str = Field(min_length=1)
    email: UserEmailRequest
    password: str
    phone: Optional[UserPhoneRequest] = None
    birthDate: Optional[str] = None
    gender: Optional[str] = None
    role: str = Field(default='customer')

    model_config = dict(
        json_schema_extra=dict(
            example=dict(
                name="Jeremy",
                lastName="Solano",
                email=dict(
                    value="example@example.com",
                    verified=False
                ),
                password="Test00001@",
                phone=dict(
                    countryAlpha2="DO",
                    prefix="+1 809",
                    value="1234456",
                    verified=False
                ),
                birthDate='2005-01-01',
                gender='M'
            )
        )
    )

    @field_validator('email')
    def validate_email(cls, value):
        if not re.match(email_regex, value.value):
            raise ValueError('Email is not valid')

        return value

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password length must be greater or equal than 8')
        if len(value) > 16:
            raise ValueError('Password length must be less or equal than 16')

        return value

    @field_validator('birthDate')
    def validate_birth_date(cls, value):
        is_valid_date = validate_date(value)

        if not is_valid_date:
            raise
        return value

    @field_validator('gender')
    def validate_gender(cls, value):
        if value not in ['M', 'F']:
            raise ValueError("Invalid gender")
        return value


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
