from datetime import datetime
from typing import TypedDict, List, Optional, NotRequired

from bson import ObjectId

from src.database.mongodb.schema.common_schemas import AttributeTypeSchema, CommonTypeSchema, MediaSchema, FeatureSchema


class ProductDetailsSchema(TypedDict):
    description: str
    characteristics: Optional[List[CommonTypeSchema]]


class ProductDatesSchema(TypedDict):
    creation: datetime
    restock: datetime


class ProductVariantsSchema(TypedDict):
    colors: Optional[List[AttributeTypeSchema]]
    sizes: Optional[List[AttributeTypeSchema]]
    # model_config = {
    #     "extra": Extra.allow
    # }


class ProductCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    store_id: Optional[str]
    name: str
    cost: float
    currency: str
    stock: int
    category_id: str
    category_name: str
    subcategory: str
    rating: Optional[float]
    imgs: Optional[List[MediaSchema]]
    dates: ProductDatesSchema
    details: ProductDetailsSchema
    variants: ProductVariantsSchema
    features: Optional[List[FeatureSchema]]
