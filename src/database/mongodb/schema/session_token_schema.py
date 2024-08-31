from datetime import datetime
from typing import TypedDict, NotRequired

from bson import ObjectId


class TokenSchema(TypedDict):
    access_token: str
    token_type: str
    expires_in: datetime
    refresh_token: str


class SessionTokenCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    username: str
    session_date: datetime
    data: TokenSchema
