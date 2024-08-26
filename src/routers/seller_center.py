from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, status, Depends

from dependencies.auth import get_current_user
from src.models.address import AddressModel
from src.models.user import BaseUserModel
from src.shared.exceptions import HttpException
from src.shared.generics import Data

seller_center_router = APIRouter()

seller_center_router.tags = ['User']


@seller_center_router.post('/seller-center/orders/place', responses={
    status.HTTP_201_CREATED: {"model": Data[AddressModel], 'description': 'Order Placed'},
})
def placer_or(address: AddressModel, current_user: Annotated[BaseUserModel, Depends(get_current_user)]):
    try:
        address.userId = ObjectId(current_user.id)

        address_id = mongo_client.addresses.insert_one(address.to_schema()).inserted_id

        address.id = str(address_id)
        address.userId = current_user.id

        return Data[str](
            data=''
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex
