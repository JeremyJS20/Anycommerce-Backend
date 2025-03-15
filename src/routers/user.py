from collections.abc import Mapping
from typing import Annotated, List, Any

from fastapi import APIRouter, status, Depends, Path
from pymongo.database import Database

from dependencies.auth import get_current_user
from dependencies.mongodb import MongoDBClient
from dependencies.stripe_client import StripeClient, StripeClientInstance
from src.database.mongodb.collection.address_collection import get_user_addresses_db, insert_address, \
    delete_address, get_user_address_by_address_id, update_address_db
from src.database.mongodb.collection.cart_collection import get_user_cart as get_user_cart_collection, \
    create_user_cart as create_user_cart_collection, add_items_to_user_cart, delete_user_cart
from src.database.mongodb.schema.address_schema import AddressCollectionSchema
from src.database.mongodb.schema.cart_schema import CartCollectionSchema, CartContentCollectionSchema
from src.models.address import AddressModel
from src.models.cart import CartContentModel, CartModel
from src.models.user import BaseUserModel
from src.shared.exceptions import HttpException
from src.shared.generics import ErrorResponse, Data, Error, MessageResponse
from src.utils.constants import ErrorsIDs, ErrorsDescriptions, ResponseDescriptions, ErrorsDescriptionsObject
from src.utils.utils import convert_currency

user_router = APIRouter()

user_router.tags = ['User']


@user_router.post('/addresses/add', responses={
    status.HTTP_400_BAD_REQUEST: {"model": Data[MessageResponse], 'description': 'Bad Request'},
    status.HTTP_201_CREATED: {"model": Data[MessageResponse], 'description': 'Address Added'},
}, status_code=status.HTTP_201_CREATED)
def add_user_address(
        address: AddressModel,
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        addresses = get_user_addresses_db(user_id=current_user.id)

        if addresses:
            if address.default:
                exists_default_address = filter(lambda ad: ad.default, addresses) is not None

                if exists_default_address:
                    raise HttpException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        error_id=ErrorsIDs.USER_ALREADY_HAVE_DEFAULT,
                        description=ErrorsDescriptionsObject[ErrorsIDs.USER_ALREADY_HAVE_DEFAULT].format('address')
                    )
        else:
            address.default = True

        address.userId = current_user.id

        insert_address(AddressCollectionSchema(**address.to_schema()))

        if address.default:
            stripe_client.customers.update(
                customer=current_user.stripeId,
                params=dict(
                    address=dict(
                        country=address.country,
                        state=address.state,
                        city=address.city,
                        postal_code=address.postalCode,
                        line1=address.address,
                        line2=address.additionalAddress
                    )
                )
            )

        return Data[MessageResponse](
            data=MessageResponse(
                message=ResponseDescriptions.RECORD_ADDED_SUCCESS.format('Address')
            ).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@user_router.get('/addresses', responses={
    status.HTTP_200_OK: {"model": Data[List[AddressModel]], 'description': 'Addresses Found'},
    status.HTTP_404_NOT_FOUND: {"model": Error[ErrorResponse], 'description': 'Addresses Not Found'},
}, status_code=status.HTTP_200_OK)
def get_user_addresses(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
):
    try:
        addresses = get_user_addresses_db(user_id=current_user.id)

        if not addresses:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('addresses')
            )

        return Data[List[AddressModel]](
            data=addresses
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@user_router.delete('/addresses/{addressId}', responses={
    status.HTTP_200_OK: {"model": Data[MessageResponse], 'description': 'Address deleted'}
}, status_code=status.HTTP_200_OK)
def delete_user_address(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        address_id: str = Path(alias='addressId'),
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        address = get_user_address_by_address_id(address_id=address_id)

        if address.default:
            stripe_client.customers.update(
                customer=current_user.stripeId,
                params=dict(
                    address=None
                )
            )

        delete_address(deleted_address_id=address_id)

        return Data[MessageResponse](
            data=MessageResponse(
                message=ResponseDescriptions.RECORD_DELETED_SUCCESS.format('Address')
            ).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@user_router.put('/addresses/change-default', responses={
    status.HTTP_200_OK: {"model": Data[MessageResponse], 'description': 'Default Address Changed'}
}, status_code=status.HTTP_200_OK)
def change_default_user_address(
        old: str,
        new: str,
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        old_default_address = get_user_address_by_address_id(address_id=old)

        if old_default_address:
            old_default_address.default = False
            update_address_db(address_id=old_default_address.id,
                              updated_address=AddressCollectionSchema(**old_default_address.to_schema()))

        new_default_address = get_user_address_by_address_id(address_id=new)

        if new_default_address:
            new_default_address.default = True
            update_address_db(address_id=new_default_address.id,
                              updated_address=AddressCollectionSchema(**new_default_address.to_schema()))

        stripe_client.customers.update(
            customer=current_user.stripeId,
            params=dict(
                address=dict(
                    country=new_default_address.countryCode,
                    state=new_default_address.state,
                    city=new_default_address.city,
                    postal_code=new_default_address.postalCode,
                    line1=new_default_address.address,
                    line2=new_default_address.additionalAddress
                )
            )
        )
        return Data[MessageResponse](
            data=MessageResponse(
                message=ResponseDescriptions.DEFAULT_ADDRESS_CHANGED
            ).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@user_router.get('/cart', responses={
    status.HTTP_200_OK: {"model": Data[List[CartContentModel]], 'description': 'Cart Found'},
    status.HTTP_404_NOT_FOUND: {"model": Error[ErrorResponse], 'description': 'Cart Not Found'},
}, status_code=status.HTTP_200_OK)
def get_user_cart(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        user_cart_db = get_user_cart_collection(user_id=current_user.id)

        if not user_cart_db:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('cart')
            )

        for cart in user_cart_db.cart:
            cart.product.cost = convert_currency(base_currency=cart.product.currency,
                                                 target_currency=current_user.preferences.currency,
                                                 amount=cart.product.cost, mongo_client=mongo_client)
            cart.product.currency = current_user.preferences.currency

            if cart.cartInfo.variants:
                for variant in cart.cartInfo.variants:
                    if variant.price:
                        variant.price = convert_currency(base_currency=cart.product.currency,
                                                         target_currency=current_user.preferences.currency,
                                                         amount=variant.price, mongo_client=mongo_client)

        return Data[List[CartContentModel]](
            data=user_cart_db.cart
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@user_router.post('/cart/create', responses={
    status.HTTP_201_CREATED: {"model": Data[MessageResponse], 'description': 'Cart created'},
    status.HTTP_400_BAD_REQUEST: {"model": Data[MessageResponse], 'description': 'Cart created'}
}, status_code=status.HTTP_201_CREATED)
def create_user_cart(
        cart: List[CartContentModel],
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
):
    try:
        user_cart = get_user_cart_collection(user_id=current_user.id)

        if user_cart:
            raise HttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_id=ErrorsIDs.USER_ALREADY_HAVE_CART,
                description=ErrorsDescriptions[ErrorsIDs.USER_ALREADY_HAVE_CART]
            )

        cart = CartModel(id=None, userId=current_user.id, cart=cart)

        create_user_cart_collection(created_cart=CartCollectionSchema(**cart.to_schema()))

        return Data[MessageResponse](
            data=MessageResponse(
                message=ResponseDescriptions.RECORD_CREATED_SUCCESS.format('Cart')
            ).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@user_router.put('/cart/update', responses={
    status.HTTP_200_OK: {"model": Data[MessageResponse], 'description': 'Cart updated'}
}, status_code=status.HTTP_200_OK)
def update_user_cart(
        new_items: List[CartContentModel],
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
):
    def item_exists_in_cart(new_item: CartContentModel, cart_items: List[CartContentModel]):
        for item in cart_items:
            if item.product.id == new_item.product.id:
                if item.cartInfo.variants == new_item.cartInfo.variants:
                    return True
        return False

    try:
        user_cart = get_user_cart_collection(user_id=current_user.id)

        if not user_cart:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('cart')
            )

        unique_new_cart_items = [
            CartContentCollectionSchema(**item.to_schema()) for item in new_items if not item_exists_in_cart(item, user_cart.cart)
        ]

        add_items_to_user_cart(cart_id=user_cart.id, new_items=unique_new_cart_items)

        return Data[MessageResponse](
            data=MessageResponse(
                message=ResponseDescriptions.RECORD_UPDATED_SUCCESS.format('Cart')
            ).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@user_router.delete('/cart/remove', responses={
    status.HTTP_200_OK: {"model": Data[MessageResponse], 'description': 'Cart updated'}
}, status_code=status.HTTP_200_OK)
def remove_user_cart(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
):
    try:
        user_cart = get_user_cart_collection(user_id=current_user.id)

        if not user_cart:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('cart')
            )

        delete_user_cart(user_id=current_user.id)

        return Data[MessageResponse](
            data=MessageResponse(
                message=ResponseDescriptions.RECORD_DELETED_SUCCESS.format('Cart')
            ).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex
