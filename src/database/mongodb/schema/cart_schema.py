from datetime import datetime
from typing import TypedDict, NotRequired, List, Union, Optional, Any

from bson import ObjectId


# class CartCollectionSchema(TypedDict):
#     _id: NotRequired[ObjectId]
#     setup_intent_id: str
#     payment_intent_id: str
#     client_secret: str
#     status: str
#     user_id: str
#     initiation_date: datetime
#     end_date: Union[None, datetime]

class CommonTypeSchema(TypedDict):
    key: str
    text: str
    value: Any
    description: Optional[str]


class MediaSchema(TypedDict):
    name: str
    size: float
    extension: str
    url: str


class AttributeTypeSchema(TypedDict):
    key: str
    value: Any
    price: Optional[int]
    available: bool
    default: bool


class CartInfoSchema(TypedDict):
    amount: int
    variants: Optional[List[AttributeTypeSchema]]


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


class ProductSchema(TypedDict):
    id: Optional[str]
    storeId: Optional[str]
    name: str
    cost: float
    currency: str
    stock: int
    category: str
    subcategory: str
    rating: Optional[float]
    imgs: Optional[List[MediaSchema]]
    dates: ProductDatesSchema
    details: ProductDetailsSchema
    variants: ProductVariantsSchema


class CartContentCollectionSchema(TypedDict):
    product: ProductSchema
    cart_info: CartInfoSchema


class CartCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    user_id: str
    cart: List[CartContentCollectionSchema]
