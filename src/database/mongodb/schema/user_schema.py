from typing import TypedDict, Optional, NotRequired

from bson import ObjectId


class EmailSchema(TypedDict):
    value: str
    verified: bool


class PhoneSchema(TypedDict):
    country: str
    prefix: str
    value: str
    verified: bool


class UserCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    stripe_id: Optional[str]
    name: str
    last_name: str
    email: EmailSchema
    password: str
    phone: Optional[PhoneSchema]
    birth_date: Optional[str]
    gender: Optional[str]
    role: str
