from datetime import datetime
from typing import TypedDict, Optional, NotRequired, Literal

from bson import ObjectId


class ConvertionRatesCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    base_currency: str
    last_update: datetime
    next_update: datetime
    convertion_rates: TypedDict
