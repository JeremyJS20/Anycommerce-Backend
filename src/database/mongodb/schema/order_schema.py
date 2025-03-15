from datetime import datetime
from typing import TypedDict, NotRequired, List, Optional

from bson import ObjectId

from src.database.mongodb.schema.common_schemas import AttributeTypeSchema, MediaSchema


class OrderDatesSchema(TypedDict):
    order: datetime
    delivery: Optional[datetime]


class CustomerInfoOrderSchema(TypedDict):
    id: str
    email: Optional[str]
    phone: Optional[str]


class ShippingInfoOrderSchema(TypedDict):
    address: str
    method: str
    tracking_number: Optional[str]


class DiscountSchema(TypedDict):
    type: str
    value: float


class ProductItemOrderSchema(TypedDict):
    id: str
    storeId: str
    name: str
    category: str
    quantity: int
    price: float
    currency: str
    variants: List[AttributeTypeSchema]
    image: MediaSchema
    discount: Optional[DiscountSchema]
    totalPrice: int


class OrderSummarySchema(TypedDict):
    currency: str
    subtotal: int
    shipping: int
    taxes: int
    total_amount: int


class BillingInfoOrderSchema(TypedDict):
    payment_method: str
    payment_intent_id: str


class OrderCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    store_id: str
    status: str
    dates: OrderDatesSchema
    user_info: CustomerInfoOrderSchema
    shipping_info: ShippingInfoOrderSchema
    billing_info: BillingInfoOrderSchema
    items: List[ProductItemOrderSchema]
    summary: OrderSummarySchema
    discount: Optional[DiscountSchema]
