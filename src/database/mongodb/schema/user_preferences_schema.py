from typing import TypedDict, Optional, NotRequired, Literal

from bson import ObjectId


class UserPreferencesCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    locale: str
    country: str
    currency: str
    theme: Literal['light', 'dark']
