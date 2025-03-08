from typing import Optional, List

from pydantic import Field

from src.models.product import ProductModel, AttributeType
from src.shared.generics import CommonModel
from src.utils.utils import ObjectIdTypeConverter


class CartInfoModel(CommonModel):
    amount: int = Field(ge=1)
    variants: Optional[List[AttributeType]] = None


class CartContentModel(CommonModel):
    product: ProductModel
    cartInfo: CartInfoModel


class CartModel(CommonModel):
    id: Optional[ObjectIdTypeConverter]
    userId: str
    cart: List[CartContentModel]
