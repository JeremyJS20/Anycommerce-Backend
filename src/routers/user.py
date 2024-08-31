from collections.abc import Mapping
from typing import Annotated, List, Any

from bson import ObjectId
from fastapi import APIRouter, status, Depends, Path
from pymongo.database import Database

from dependencies.auth import get_current_user
from dependencies.mongodb import MongoDBClient
from dependencies.stripe_client import StripeClient, StripeClientInstance
from src.models.address import AddressModel
from src.models.request.user import CartRequest, CartModelRequest, PaymentMethodCardRequest
from src.models.responses.user import CartResponse, AddressResponse
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
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient()),
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        address.userId = ObjectId(current_user.id)

        user_addresses_db = mongo_client.addresses.find(
            {'user_id': ObjectId(current_user.id)})

        user_addresses = [ad for ad in user_addresses_db]

        if len(user_addresses) > 0:
            if address.default:
                exists_default_address = filter(lambda ad: ad.default, user_addresses) is not None

                if exists_default_address:
                    raise HttpException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        error_id=ErrorsIDs.USER_ALREADY_HAVE_DEFAULT,
                        description=ErrorsDescriptionsObject[ErrorsIDs.USER_ALREADY_HAVE_DEFAULT].format('address')
                    )
        else:
            address.default = True

        mongo_client.addresses.insert_one(address.to_schema())

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
    status.HTTP_200_OK: {"model": Data[List[AddressResponse]], 'description': 'Addresses Found'},
    status.HTTP_404_NOT_FOUND: {"model": Error[ErrorResponse], 'description': 'Addresses Not Found'},
}, status_code=status.HTTP_200_OK)
def get_user_addresses(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        addresses_db = mongo_client.addresses.find({'user_id': ObjectId(current_user.id)})

        addresses = [AddressResponse(
            id=str(address['_id']),
            country=address['country'],
            state=address['state'],
            city=address['city'],
            postalCode=address['postal_code'],
            address=address['address'],
            additionalAddress=address.get('additionalAddress'),
            default=address['default']
        ) for address in addresses_db]

        if len(addresses) <= 0:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('addresses')
            )

        return Data[List[AddressResponse]](
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
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient()),
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:

        is_default_address = mongo_client.addresses.find_one(
            {'user_id': ObjectId(current_user.id), 'default': True}) is not None

        if is_default_address:
            stripe_client.customers.update(
                customer=current_user.stripeId,
                params=dict(
                    address=None
                )
            )

        mongo_client.addresses.delete_one({"_id": ObjectId(address_id), 'user_id': ObjectId(current_user.id)})

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
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient()),
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        mongo_client.addresses.update_one(
            {"_id": ObjectId(old), 'user_id': ObjectId(current_user.id)},
            {"$set": dict(
                default=False
            )}
        )

        address = mongo_client.addresses.find_one_and_update(
            {"_id": ObjectId(new), 'user_id': ObjectId(current_user.id)},
            {"$set": dict(
                default=True
            )},
            return_document=True
        )

        stripe_client.customers.update(
            customer=current_user.stripeId,
            params=dict(
                address=dict(
                    country=address['country'],
                    state=address['state'],
                    city=address['city'],
                    postal_code=address['postal_code'],
                    line1=address['address'],
                    line2=address.get('additional_address')
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
    status.HTTP_200_OK: {"model": Data[List[CartResponse]], 'description': 'Cart Found'},
    status.HTTP_404_NOT_FOUND: {"model": Error[ErrorResponse], 'description': 'Cart Not Found'},
}, status_code=status.HTTP_200_OK)
def get_user_cart(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        user_cart_db = mongo_client.cart.find_one({'user_id': current_user.id})

        if not user_cart_db:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('cart')
            )

        for cart in user_cart_db['cart']:
            cart['product']['cost'] = convert_currency(base_currency=cart['product']['currency'],
                                                       target_currency=current_user.preferences.currency,
                                                       amount=cart['product']['cost'], mongo_client=mongo_client)
            cart['product']['currency'] = current_user.preferences.currency

            if cart['cart_info']['variants']:
                for variant in cart['cart_info']['variants']:
                    if variant['price']:
                        variant['price'] = convert_currency(base_currency=cart['product']['currency'],
                                                            target_currency=current_user.preferences.currency,
                                                            amount=variant['price'], mongo_client=mongo_client)

        user_cart = [CartResponse(
            product=cart['product'],
            cartInfo=cart['cart_info']
        ).to_json() for cart in user_cart_db['cart']]

        return Data[List[CartResponse]](
            data=user_cart
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
        cart: List[CartModelRequest],
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        user_cart = mongo_client.cart.find_one({'user_id': current_user.id})

        if user_cart:
            raise HttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_id=ErrorsIDs.USER_ALREADY_HAVE_CART,
                description=ErrorsDescriptions[ErrorsIDs.USER_ALREADY_HAVE_CART]
            )

        mongo_client.cart.insert_one(CartRequest(
            userId=current_user.id,
            cart=cart
        ).to_schema())

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
        new_items: List[CartModelRequest],
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    def item_exists_in_cart(new_item, cart_items):
        for item in cart_items:
            if item["product"]["id"] == new_item["product"]["id"]:
                if item["cart_info"]["variants"] == new_item["cart_info"]["variants"]:
                    return True
        return False

    try:
        user_cart = mongo_client.cart.find_one({'user_id': current_user.id})

        if not user_cart:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('cart')
            )

        unique_new_cart_items = [
            item.to_schema() for item in new_items if not item_exists_in_cart(item.to_schema(), user_cart['cart'])
        ]

        mongo_client.cart.update_one(
            {'user_id': current_user.id},
            {"$addToSet": {"cart": {"$each": unique_new_cart_items}}}
        )

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
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        user_cart = mongo_client.cart.find_one({'user_id': current_user.id})

        if not user_cart:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('cart')
            )

        mongo_client.cart.delete_one({'user_id': current_user.id})

        return Data[MessageResponse](
            data=MessageResponse(
                message=ResponseDescriptions.RECORD_DELETED_SUCCESS.format('Cart')
            ).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex
