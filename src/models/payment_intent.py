from datetime import datetime
from typing import Optional, Union

from src.shared.generics import CommonModel
from src.utils.utils import ObjectIdTypeConverter


class PaymentIntentModel(CommonModel):
    id: Optional[ObjectIdTypeConverter]
    setupIntentId: str
    paymentIntentId: str
    clientSecret: str
    status: str
    userId: str
    initiationDate: datetime
    endDate: Optional[datetime]
