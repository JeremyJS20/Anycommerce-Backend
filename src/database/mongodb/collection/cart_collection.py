from typing import Optional, Mapping, Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import UpdateResult

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.cart_schema import CartCollectionSchema
from src.database.mongodb.schema.payment_intent_schema import PaymentIntentCollectionSchema
from src.models.cart import CartModel
from src.models.payment_intent import PaymentIntentModel
from src.utils.constants import PaymentIntentStatus
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[CartCollectionSchema] = mongo_client.cart


def get_user_cart(user_id: str) -> Optional[CartModel]:
    try:
        cart = collection.find_one({'user_id': user_id})

        if not cart:
            return None

        return CartModel(**snake_to_camel_case(cart))
    except Exception as e:
        raise e


# def update_payment_intent(payment_intent_id: str, updated_payment_intent: PaymentIntentCollectionSchema) -> bool:
#     try:
#         updated_payment_intent['_id'] = ObjectId(payment_intent_id)
#
#         updated_payment_intent: UpdateResult = mongo_client.payment_intent.update_one(
#             {"_id": ObjectId(payment_intent_id)},
#             {"$set": updated_payment_intent}
#         )
#
#         return updated_payment_intent.modified_count > 0
#     except Exception as e:
#         raise e
#
#
# def insert_payment_intent(inserted_payment_intent: PaymentIntentCollectionSchema) -> Optional[str]:
#     try:
#         inserted_payment_intent['_id'] = ObjectId()
#
#         inserted_payment_intent_id = collection.insert_one(inserted_payment_intent).inserted_id
#
#         if not inserted_payment_intent_id:
#             return None
#
#         return str(inserted_payment_intent_id)
#     except Exception as e:
#         raise e
