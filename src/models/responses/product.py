from typing import Optional, List

from src.models.common import MediaModel, FeatureModel
from src.models.product import ProductDetails, ProductVariants, ProductDates
from src.models.responses.review import ReviewResponse
from src.shared.generics import CommonResponseModel


class ProductsResponse(CommonResponseModel):
    id: str
    name: str
    cost: float
    currency: str
    stock: int
    categoryId: str
    categoryName: str
    subcategory: str
    rating: Optional[float] = None
    imgs: Optional[List[MediaModel]] = None
    features: Optional[List[FeatureModel]] = None


class ProductResponse(CommonResponseModel):
    id: str
    storeId: str
    name: str
    cost: float
    currency: str
    stock: int
    categoryId: str
    categoryName: str
    subcategory: str
    rating: Optional[float] = None
    imgs: Optional[List[MediaModel]] = None
    dates: ProductDates
    details: ProductDetails
    variants: Optional[ProductVariants] = None
    features: Optional[List[FeatureModel]] = None
    reviews: Optional[List[ReviewResponse]] = None


class ProductResponseAdditionalData(CommonResponseModel):
    totalReviews: int
