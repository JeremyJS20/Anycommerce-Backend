from datetime import datetime
from typing import TypedDict, NotRequired, List, Union

from bson import ObjectId


class PaymentIntentCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    setup_intent_id: str
    payment_intent_id: str
    client_secret: str
    status: str
    user_id: str
    initiation_date: datetime
    end_date: Union[None, datetime]
