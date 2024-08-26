from datetime import datetime
from typing import Optional, List

from pydantic import Field

from src.models.common import MediaModel
from src.shared.generics import CommonModel


class ReviewRequest(CommonModel):
    title: str = Field(min_length=1, max_length=50, examples=["Title example"])
    opinion: str = Field(min_length=1, max_length=500, examples=["Lorem ipsum dolor sit amet, consectetur adipiscing "
                                                                 "elit, sed do eiusmod tempor incididunt ut labore et "
                                                                 "dolore magna aliqua. Ut enim ad minim veniam, quis "
                                                                 "nostrud exercitation ullamco laboris nisi ut aliquip"
                                                                 " ex ea commodo consequat."])
    rating: float = Field(gt=0, le=5, default=1)
    date: datetime
    userId: Optional[str] = Field(default=None, min_length=1, max_length=50)
    productId: Optional[str] = Field(default=None, min_length=1, max_length=50)
    media: Optional[List[MediaModel]] = None
