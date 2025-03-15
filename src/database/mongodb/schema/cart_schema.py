from typing import TypedDict, NotRequired, List, Optional

from bson import ObjectId

from src.database.mongodb.schema.common_schemas import AttributeTypeSchema
from src.database.mongodb.schema.product_schema import ProductCollectionSchema


class CartInfoSchema(TypedDict):
    amount: int
    variants: Optional[List[AttributeTypeSchema]]


class CartContentCollectionSchema(TypedDict):
    product: ProductCollectionSchema
    cart_info: CartInfoSchema


class CartCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    user_id: str
    cart: List[CartContentCollectionSchema]
