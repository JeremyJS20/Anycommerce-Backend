from datetime import datetime
from typing import TypedDict, NotRequired, List, Union, Optional

from bson import ObjectId


class AddressCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    user_id: Optional[str]
    country: str
    country_code: str
    state: str
    state_code: str
    city: str
    postal_code: str
    address: str
    additional_address: Optional[str]
    default: bool
