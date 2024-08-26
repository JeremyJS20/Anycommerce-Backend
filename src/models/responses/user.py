from typing import Optional

from src.models.common import MediaModel
from src.models.product import ProductModel
from src.models.request.user import CartInfoModel
from src.shared.generics import CommonModel


class UserResponse(CommonModel):
    id: str
    name: str
    lastName: str
    profilePhoto: Optional[MediaModel] = None


class CartResponse(CommonModel):
    product: ProductModel
    cartInfo: CartInfoModel


class AddressResponse(CommonModel):
    id: Optional[str] = None
    country: str
    state: str
    city: str
    postalCode: str
    address: str
    additionalAddress: Optional[str] = None
    default: bool


class PaymentMethodTypeCardBasicModelResponse(CommonModel):
    stripeId: str
    company: str
    name: str
    ending: str
    expirationDate: str


class PaymentMethodCardResponse(CommonModel):
    userId: str
    type: str
    default: bool
    methodInfo: PaymentMethodTypeCardBasicModelResponse
