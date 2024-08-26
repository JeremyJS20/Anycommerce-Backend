from datetime import datetime
from enum import Enum
from typing import Optional, List, Literal

from pydantic import Field

from src.models.common import MediaModel
from src.models.product import ProductVariants, AttributeType
from src.shared.generics import CommonModel
from src.utils.constants import OrderStatus


class OrderDatesModel(CommonModel):
    order: datetime
    delivery: Optional[datetime] = None


class CustomerInfoOrderModel(CommonModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None


class ShippingInfoOrderModel(CommonModel):
    address: str
    method: Literal["standard", "express"]
    trackingNumber: Optional[str] = None


class Discount(CommonModel):
    type: Literal["percentage", "fixed"]
    value: float


class ProductItemOrderModel(CommonModel):
    id: str
    storeId: str
    name: str
    category: str
    quantity: int
    price: float
    currency: str
    variants: List[AttributeType]
    image: MediaModel
    discount: Optional[Discount] = None
    totalPrice: float


class OrderSummaryModel(CommonModel):
    currency: str
    subtotal: float
    shipping: float
    taxes: float
    totalAmount: float


class BillingInfoOrderModel(CommonModel):
    paymentMethod: str
    paymentIntentId: str


class OrderModel(CommonModel):
    storeId: str
    status: str = Field(min_length=1, default=OrderStatus.ORDER_PLACED.value)
    dates: OrderDatesModel
    userInfo: CustomerInfoOrderModel
    shippingInfo: ShippingInfoOrderModel
    billingInfo: BillingInfoOrderModel
    items: List[ProductItemOrderModel]
    summary: OrderSummaryModel
    discount: Optional[Discount] = None
