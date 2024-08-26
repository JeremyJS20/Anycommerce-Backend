import re
from datetime import datetime
from typing import Optional, Union, Literal

from pydantic import BaseModel, field_validator, Field

from src.models.submodels.email import EmailModel
from src.models.submodels.phone import PhoneModel
from src.shared.generics import CommonModel
from src.utils.regex import email_regex
from src.utils.utils import camel_to_snake_case, validate_date


class CommonMethodsModel:
    def to_schema(self: BaseModel) -> dict:
        return camel_to_snake_case(self.model_dump())


class CreateUserModel(CommonModel):
    stripeId: Optional[None] = None
    name: str = Field(min_length=1)
    lastName: str = Field(min_length=1)
    email: EmailModel
    password: str
    phone: Optional[PhoneModel] = None
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


class UserPreferencesModel(CommonModel):
    locale: str
    country: str
    currency: str
    theme: Literal['light', 'dark']


class UserPreferencesModelWrapper(CommonModel):
    id: str
    userId: str
    preferences: UserPreferencesModel


class BaseUserModel(CommonModel):
    id: str
    stripeId: str
    name: str
    lastName: str
    email: EmailModel
    phone: Optional[PhoneModel] = None
    role: str
    preferences: Union[UserPreferencesModel, None]

    model_config = dict(
        json_schema_extra=dict(
            example=dict(
                id="507f1f77bcf86cd799439011",
                name="Jeremy",
                lastName="Solano",
                email=dict(
                    value="example@example.com",
                    verified=False
                )
            )
        )
    )
