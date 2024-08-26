from typing import Optional, List

from pydantic import Field

from src.models.common import MediaModel
from src.models.product import ProductDetails, ProductVariants, ProductDates
from src.models.responses.review import ReviewResponse
from src.shared.generics import CommonModel


class ProductDetailResponse(CommonModel):
    id: Optional[str] = None
    name: str = Field(min_length=1)
    cost: float = Field(gt=0)
    currency: str = Field(min_length=1)
    stock: int = Field(gt=0)
    category: str = Field(min_length=1)
    subcategory: str = Field(min_length=1)
    rating: Optional[float] = None
    imgs: Optional[List[MediaModel]] = Field(default=[MediaModel().to_json()])
    dates: ProductDates
    details: ProductDetails
    variants: ProductVariants
    reviews: Optional[List[ReviewResponse]] = None
