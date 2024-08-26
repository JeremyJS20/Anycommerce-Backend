from datetime import datetime
from typing import Optional, List

from src.models.common import MediaModel
from src.models.responses.user import UserResponse
from src.shared.generics import CommonModel


class ReviewResponse(CommonModel):
    id: str
    title: str
    opinion: str
    rating: float
    date: datetime
    customer: UserResponse
    media: Optional[List[MediaModel]]
