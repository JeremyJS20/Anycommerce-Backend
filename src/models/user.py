from typing import Optional, Union, Literal

from pydantic import BaseModel

from src.models.submodels.email import EmailModel
from src.models.submodels.phone import PhoneModel
from src.shared.generics import CommonModel
from src.utils.utils import camel_to_snake_case, ObjectIdTypeConverter


class CommonMethodsModel:
    def to_schema(self: BaseModel) -> dict:
        return camel_to_snake_case(self.model_dump())


class UserModel(CommonModel):
    id: ObjectIdTypeConverter
    stripeId: Optional[str] = None
    name: str
    lastName: str
    email: EmailModel
    password: str
    phone: Optional[PhoneModel] = None
    birthDate: Optional[str] = None
    gender: Optional[str] = None
    role: str


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
