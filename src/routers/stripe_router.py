import datetime
import uuid
from typing import Annotated, List, Mapping, Any, Union

import requests
from bson import ObjectId
from fastapi import APIRouter, Depends, Path
from fastapi import status
from pymongo.database import Database
from stripe import StripeClient, CustomerPaymentMethodService, SetupIntentService, PaymentIntentService, CardError
from stripe.tax import CalculationService

from dependencies.auth import get_current_user
from dependencies.mongodb import MongoDBClient
from dependencies.stripe_client import StripeClientInstance
from src.env_variables.env import env_variables
from src.models.product import ProductModel
from src.models.request.order import OrderModel, OrderDatesModel, CustomerInfoOrderModel, ShippingInfoOrderModel, \
    BillingInfoOrderModel, ProductItemOrderModel, OrderSummaryModel
from src.models.request.stripe_integration import CalculateTaxesRequest
from src.models.responses.stripe_integration import SetupIntentResponse, PaymentMethodResponse, CalculateTaxesResponse, \
    PlaceOrderRequest
from src.models.responses.user import CartResponse
from src.models.user import BaseUserModel
from src.shared.exceptions import HttpException
from src.shared.generics import Data, Error, ErrorResponse, MessageResponse, MessageWithStatusResponse
from src.utils.constants import ErrorsIDs, ErrorsDescriptionsObject, PaymentIntentStatus, ResponseDescriptions, \
    StripeErrorsIDs, StripeErrorsDescriptionsObject
from src.utils.utils import convert_currency

stripe_router = APIRouter(tags=['Stripe integration'])
currency_convertion_api_url = env_variables.currency_convertion_api_url


@stripe_router.post('/payment-intent/setup', responses={
    status.HTTP_201_CREATED: {"model": Data[SetupIntentResponse], 'description': 'Setup intent created'},
}, status_code=status.HTTP_201_CREATED)
def setup_stripe_payment_intent(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient()),
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        payment_intent_initiated = mongo_client.payment_intent.find_one(
            {'user_id': current_user.id, 'status': PaymentIntentStatus.INITIATED.value})

        if payment_intent_initiated:
            current_setup_intent = stripe_client.setup_intents.retrieve(payment_intent_initiated['setup_intent_id'])

            if current_setup_intent.status == 'succeeded':
                current_setup_intent = stripe_client.setup_intents.create(
                    params=SetupIntentService.CreateParams(
                        payment_method_types=['card'],
                        customer=current_user.stripeId
                    )
                )

                intent_model = SetupIntentResponse(
                    setupIntentId=current_setup_intent.id,
                    paymentIntentId=payment_intent_initiated['payment_intent_id'],
                    clientSecret=current_setup_intent.client_secret,
                    userId=current_user.id,
                    status=PaymentIntentStatus.INITIATED.value,
                    initiationDate=datetime.datetime.now(),
                    endDate=None
                )

                mongo_client.payment_intent.update_one(
                    {"setup_intent_id": payment_intent_initiated['setup_intent_id']},
                    {"$set": dict(
                        setup_intent_id=current_setup_intent.id,
                        client_secret=current_setup_intent.client_secret
                    )}
                )

                return Data[SetupIntentResponse](
                    data=intent_model
                )
            else:

                intent_model = SetupIntentResponse(
                    setupIntentId=payment_intent_initiated['setup_intent_id'],
                    paymentIntentId=payment_intent_initiated['payment_intent_id'],
                    clientSecret=payment_intent_initiated['client_secret'],
                    userId=current_user.id,
                    status=PaymentIntentStatus.INITIATED.value,
                    initiationDate=datetime.datetime.now(),
                    endDate=None
                )

                mongo_client.payment_intent.update_one(
                    {"setup_intent_id": payment_intent_initiated['setup_intent_id']},
                    {"$set": dict(
                        initiation_date=datetime.datetime.now()
                    )}
                )

                return Data[SetupIntentResponse](
                    data=intent_model
                )

        setup_intent = stripe_client.setup_intents.create(
            params=SetupIntentService.CreateParams(
                payment_method_types=['card'],
                customer=current_user.stripeId
            )
        )

        user_cart_db = mongo_client.cart.find_one({'user_id': current_user.id})

        user_cart: List[CartResponse] = [CartResponse(
            product=cart['product'],
            cartInfo=cart['cart_info']
        ) for cart in user_cart_db['cart']]

        amount = sum([int((prod.product.cost + sum(
            [variant.price for variant in prod.cartInfo.variants if variant.price])) * prod.cartInfo.amount)
                      for prod in user_cart])

        payment_intent = stripe_client.payment_intents.create(
            params=PaymentIntentService.CreateParams(
                payment_method_types=['card'],
                customer=current_user.stripeId,
                amount=amount * 100,
                currency=current_user.preferences.currency
            )
        )

        intent_model = SetupIntentResponse(
            setupIntentId=setup_intent.id,
            paymentIntentId=payment_intent.id,
            clientSecret=setup_intent.client_secret,
            userId=current_user.id,
            status=PaymentIntentStatus.INITIATED.value,
            initiationDate=datetime.datetime.now(),
            endDate=None
        )

        mongo_client.payment_intent.insert_one(intent_model.to_schema())

        return Data[SetupIntentResponse](
            data=intent_model
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@stripe_router.delete('/payment-intent/{setupIntentId}/remove', responses={
    status.HTTP_200_OK: {"model": Data[MessageResponse], 'description': 'Payment intent removed'},
    status.HTTP_404_NOT_FOUND: {"model": Data[MessageResponse], 'description': 'Payment intent not found'},
}, status_code=status.HTTP_200_OK)
def remove_stripe_payment_intent(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient()),
        setup_intent_id: str = Path(alias="setupIntentId", min_length=1),
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        payment_intent_db = mongo_client.payment_intent.find_one(
            {'setup_intent_id': setup_intent_id, 'user_id': current_user.id})

        if not payment_intent_db:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptionsObject[ErrorsIDs.NO_RECORDS_FOUND].format('Payment intent')
            )

        mongo_client.payment_intent.delete_one({'setup_intent_id': setup_intent_id, 'user_id': current_user.id})

        # payment_intent_stripe = stripe_client.payment_intents.retrieve(payment_intent_db['payment_intent_id'])

        # if payment_intent_stripe.status != 'canceled':
        stripe_client.payment_intents.cancel(payment_intent_db['payment_intent_id'])

        return Data[MessageResponse](
            data=MessageResponse(
                message=ResponseDescriptions.RECORD_DELETED_SUCCESS.format('Payment intent')
            )
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@stripe_router.get('/user/payment-method', responses={
    status.HTTP_200_OK: {"model": Data[List[PaymentMethodResponse]], 'description': 'Payment Methods Found'},
    status.HTTP_404_NOT_FOUND: {"model": Error[ErrorResponse], 'description': 'Payment Methods  Not Found'},
}, status_code=status.HTTP_200_OK)
def get_payment_methods(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        payment_methods = stripe_client.customers.payment_methods.list(
            customer=current_user.stripeId,
            params=CustomerPaymentMethodService.ListParams(
                type='card'
            )
        ).data

        if len(payment_methods) <= 0:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptionsObject[ErrorsIDs.NO_RECORDS_FOUND].format('Payment methods')
            )

        payment_methods = [PaymentMethodResponse(
            id=pm.id,
            default=False,
            type=pm.type,
            brand=pm.card.brand,
            ending=pm.card.last4,
            expirationDate=f'{pm.card.exp_month:02}/{pm.card.exp_year}' if len(
                str(pm.card.exp_month)) <= 1 else f'{pm.card.exp_month}/{pm.card.exp_year}'
        ) for pm in payment_methods]

        return Data[List[PaymentMethodResponse]](
            data=payment_methods
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@stripe_router.post('/taxes/calculate', responses={
    status.HTTP_200_OK: {"model": Data[CalculateTaxesResponse], 'description': 'Taxes calculated'},
}, status_code=status.HTTP_200_OK)
def calculate_taxes(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        calculate_taxes_request: CalculateTaxesRequest,
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient()),
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        user_cart_db = mongo_client.cart.find_one({'user_id': current_user.id})

        user_cart: List[CartResponse] = [CartResponse(
            product=cart['product'],
            cartInfo=cart['cart_info']
        ) for cart in user_cart_db['cart']]

        line_items_stripe = [CalculationService.CreateParamsLineItem(
            amount=convert_currency(base_currency=prod.product.currency,
                                    target_currency=current_user.preferences.currency,
                                    amount=int((prod.product.cost + sum(
                                        [variant.price for variant in prod.cartInfo.variants if
                                         variant.price])) * prod.cartInfo.amount),
                                    mongo_client=mongo_client
                                    ),
            reference=f'{prod.product.name}, {', '.join([variant.value for variant in prod.cartInfo.variants])}.'
        ) for prod in user_cart]

        user_address_db = mongo_client.addresses.find_one({'_id': ObjectId(calculate_taxes_request.addressId)})

        tax_calculation = stripe_client.tax.calculations.create(
            params=CalculationService.CreateParams(
                currency="USD",
                customer_details=CalculationService.CreateParamsCustomerDetails(
                    address=CalculationService.CreateParamsCustomerDetailsAddress(
                        postal_code=user_address_db['postal_code'],
                        country=user_address_db['country']
                    ),
                    address_source='shipping'
                ),
                line_items=line_items_stripe
            )
        )

        return Data[CalculateTaxesResponse](
            data=CalculateTaxesResponse(
                total=tax_calculation.amount_total,
                inclusiveTaxes=tax_calculation.tax_amount_inclusive,
                exclusiveTaxes=tax_calculation.tax_amount_exclusive
            )
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@stripe_router.post('/place-order', responses={
    status.HTTP_200_OK: {"model": Data[MessageResponse], 'description': 'Order placed'},
    status.HTTP_202_ACCEPTED: {"model": Data[MessageWithStatusResponse], 'description': 'Order being processed'},
}, status_code=status.HTTP_200_OK)
def place_order(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        place_order_request: PlaceOrderRequest,
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient()),
        stripe_client: StripeClient = Depends(StripeClientInstance())
):
    try:
        user_cart_db = mongo_client.cart.find_one({'user_id': current_user.id})
        user_address_db = mongo_client.addresses.find_one(
            {'_id': ObjectId(place_order_request.shippingAddress), 'user_id': ObjectId(current_user.id)})
        payment_intent_db = mongo_client.payment_intent.find_one(
            {'user_id': current_user.id, 'status': PaymentIntentStatus.INITIATED.value})

        user_cart: List[CartResponse] = [CartResponse(
            product=ProductModel.to_model(cart['product']),
            cartInfo=cart['cart_info']
        ) for cart in user_cart_db['cart']]

        orders: List[OrderModel] = []

        for product in user_cart:
            existent_store_order: Union[List[OrderModel], OrderModel] = list(
                filter(lambda order: order.storeId == product.product.storeId, orders))

            if len(existent_store_order) > 0:
                existent_store_order = existent_store_order[0]

                existent_store_order.items.append(
                    ProductItemOrderModel(
                        id=product.product.id,
                        image=product.product.imgs[0] if len(product.product.imgs) > 0 else None,
                        storeId=product.product.storeId,
                        name=product.product.name,
                        category=product.product.category,
                        quantity=product.cartInfo.amount,
                        price=product.product.cost,
                        currency=product.product.currency,
                        variants=product.cartInfo.variants,
                        totalPrice=int((product.product.cost + sum(
                            [variant.price for variant in product.cartInfo.variants if
                             variant.price])) * product.cartInfo.amount)
                    ))

                total = int((product.product.cost + sum(
                    [variant.price for variant in product.cartInfo.variants if
                     variant.price])) * product.cartInfo.amount)

                if product.product.currency != current_user.preferences.currency:
                    subtotal_convertion = requests.get(
                        url=f'{currency_convertion_api_url}/pair/{product.product.currency}/{current_user.preferences.currency}/{total}')

                    total = round(subtotal_convertion.json()['conversion_result'])

                existent_store_order.summary.subtotal += total

            else:
                total = int((product.product.cost + sum(
                    [variant.price for variant in product.cartInfo.variants if
                     variant.price])) * product.cartInfo.amount)

                if product.product.currency != current_user.preferences.currency:
                    subtotal_convertion = requests.get(
                        url=f'{currency_convertion_api_url}/pair/{product.product.currency}/{current_user.preferences.currency}/{total}')

                    total = round(subtotal_convertion.json()['conversion_result'])

                existent_store_order = OrderModel(
                    storeId=product.product.storeId,
                    dates=OrderDatesModel(
                        order=datetime.datetime.now()
                    ),
                    userInfo=CustomerInfoOrderModel(
                        id=current_user.id,
                        email=place_order_request.contactInfo.email,
                        phone=place_order_request.contactInfo.phone
                    ),
                    shippingInfo=ShippingInfoOrderModel(
                        address=place_order_request.shippingAddress,
                        method='express',
                        trackingNumber=str(uuid.uuid4())
                    ),
                    billingInfo=BillingInfoOrderModel(
                        paymentIntentId=payment_intent_db['payment_intent_id'],
                        paymentMethod=place_order_request.paymentMethod
                    ),
                    items=[
                        ProductItemOrderModel(
                            id=product.product.id,
                            image=product.product.imgs[0] if len(product.product.imgs) > 0 else None,
                            storeId=product.product.storeId,
                            name=product.product.name,
                            category=product.product.category,
                            quantity=product.cartInfo.amount,
                            price=product.product.cost,
                            currency=product.product.currency,
                            variants=product.cartInfo.variants,
                            totalPrice=int((product.product.cost + sum(
                                [variant.price for variant in product.cartInfo.variants if
                                 variant.price])) * product.cartInfo.amount)
                        )
                    ],
                    summary=OrderSummaryModel(
                        currency=current_user.preferences.currency,
                        subtotal=total,
                        shipping=0,
                        taxes=0,
                        totalAmount=total
                    )
                )

                orders.append(existent_store_order)

        for order in orders:
            line_items_stripe = [
                CalculationService.CreateParamsLineItem(
                    amount=int(order.summary.subtotal),
                    reference=f'{order.storeId}',
                    tax_behavior='exclusive'
                )]

            tax_calculation = stripe_client.tax.calculations.create(
                params=CalculationService.CreateParams(
                    currency=current_user.preferences.currency,
                    customer_details=CalculationService.CreateParamsCustomerDetails(
                        address=CalculationService.CreateParamsCustomerDetailsAddress(
                            postal_code=user_address_db['postal_code'],
                            country=user_address_db['country']
                        ),
                        address_source='shipping'
                    ),
                    line_items=line_items_stripe
                )
            )

            order.summary.taxes = tax_calculation.tax_amount_exclusive or tax_calculation.tax_amount_inclusive
            order.summary.totalAmount = (order.summary.subtotal + order.summary.taxes + order.summary.shipping)

        amount_to_pay_in_cents = int(sum([
            order.summary.totalAmount for order in orders
        ]) * 100)

        stripe_client.payment_intents.update(
            payment_intent_db['payment_intent_id'],
            params=PaymentIntentService.UpdateParams(
                payment_method_types=['card'],
                customer=current_user.stripeId,
                amount=amount_to_pay_in_cents,
                currency=current_user.preferences.currency,
                payment_method=place_order_request.paymentMethod
            )
        )

        payment_intent = stripe_client.payment_intents.confirm(
            payment_intent_db['payment_intent_id'],
            params=PaymentIntentService.ConfirmParams(
                payment_method=place_order_request.paymentMethod
            )
        )

        # if payment_intent.status.upper() == PaymentIntentStatus.PROCESSING.value:
        #     mongo_client.payment_intent.update_one(
        #         {"payment_intent_id": payment_intent_db['payment_intent_id']},
        #         {"$set": dict(
        #             status=PaymentIntentStatus.PROCESSING.value
        #         )}
        #     )
        #
        #     return JSONResponse(
        #         status_code=status.ACCEPTED.value,
        #         content=Data[MessageResponse](
        #             data=MessageWithStatusResponse(
        #                 status=f'{PaymentIntentStatus.PROCESSING.value}_PAYMENT'.lower(),
        #                 message=ResponseDescriptions.PROCESSING_PAYMENT
        #             )
        #         ).to_json()
        #     )

        if payment_intent.status.upper() != PaymentIntentStatus.SUCCESSFUL.value:
            payment_intent = stripe_client.payment_intents.create(
                params=PaymentIntentService.CreateParams(
                    payment_method_types=['card'],
                    customer=current_user.stripeId,
                    amount=1,
                    currency=current_user.preferences.currency
                )
            )

            mongo_client.payment_intent.update_one(
                {'user_id': current_user.id, 'status': PaymentIntentStatus.INITIATED.value},
                {"$set": dict(
                    payment_intent_id=payment_intent.id
                )}
            )

            raise HttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_id=0,
                description="test"
            )

        mongo_client.payment_intent.update_one(
            {"payment_intent_id": payment_intent_db['payment_intent_id']},
            {"$set": dict(
                status=PaymentIntentStatus.SUCCESSFUL.value,
                end_date=datetime.datetime.now()
            )}
        )

        mongo_client.orders.insert_many([order.to_schema() for order in orders])

        for order in orders:
            for product in order.items:
                product_db = mongo_client.product.find_one({'_id': ObjectId(product.id)})

                if product_db:
                    mongo_client.product.update_one(
                        {"_id": ObjectId(product.id)},
                        {"$set": dict(
                            stock=product_db['stock'] - product.quantity
                        )}
                    )

        mongo_client.cart.delete_one({'user_id': current_user.id})

        return Data[MessageResponse](
            data=MessageResponse(message='testing')
        )

    except HttpException as ex:
        raise ex

    except CardError as ex:
        payment_intent = stripe_client.payment_intents.create(
            params=PaymentIntentService.CreateParams(
                payment_method_types=['card'],
                customer=current_user.stripeId,
                amount=1,
                currency=current_user.preferences.currency
            )
        )

        mongo_client.payment_intent.update_one(
            {'user_id': current_user.id, 'status': PaymentIntentStatus.INITIATED.value},
            {"$set": dict(
                payment_intent_id=payment_intent.id
            )}
        )

        error_id = StripeErrorsIDs.__dict__.get(
            ex.error.decline_code.upper() if ex.error.decline_code else ex.error.code.upper())
        error_description = StripeErrorsDescriptionsObject[error_id]

        raise HttpException(
            status_code=ex.http_status,
            error_id=error_id,
            description=error_description
        )

    except Exception as ex:
        raise ex
