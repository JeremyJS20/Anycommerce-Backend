from typing import Optional, Mapping, Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.payment_intent_schema import PaymentIntentCollectionSchema
from src.models.payment_intent import PaymentIntentModel
from src.utils.constants import PaymentIntentStatus
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[PaymentIntentCollectionSchema] = mongo_client.payment_intent


def get_user_payment_intent_by_status(user_id: str, status: PaymentIntentStatus) -> Optional[PaymentIntentModel]:
    try:
        payment_intent = collection.find_one({'user_id': user_id, 'status': status.value})

        if not payment_intent:
            return None

        return PaymentIntentModel(**snake_to_camel_case(payment_intent))
    except Exception as e:
        raise e


def get_user_payment_intent_by_setup_id(user_id: str, setup_intent_id: str) -> Optional[PaymentIntentModel]:
    try:
        payment_intent = collection.find_one({'user_id': user_id, 'setup_intent_id': setup_intent_id})

        if not payment_intent:
            return None

        return PaymentIntentModel(**snake_to_camel_case(payment_intent))
    except Exception as e:
        raise e


def update_payment_intent(payment_intent_id: str, updated_payment_intent: PaymentIntentCollectionSchema) -> bool:
    try:
        updated_payment_intent['_id'] = ObjectId(payment_intent_id)

        updated_payment_intent: UpdateResult = mongo_client.payment_intent.update_one(
            {"_id": ObjectId(payment_intent_id)},
            {"$set": updated_payment_intent}
        )

        return updated_payment_intent.modified_count > 0
    except Exception as e:
        raise e


def delete_payment_intent(deleted_payment_intent_id: str) -> bool:
    try:
        deleted_payment_intent: DeleteResult = mongo_client.payment_intent.delete_one(
            {"_id": ObjectId(deleted_payment_intent_id)},
        )

        return deleted_payment_intent.deleted_count > 0
    except Exception as e:
        raise e


def insert_payment_intent(inserted_payment_intent: PaymentIntentCollectionSchema) -> Optional[str]:
    try:
        inserted_payment_intent['_id'] = ObjectId()

        inserted_payment_intent_id = collection.insert_one(inserted_payment_intent).inserted_id

        if not inserted_payment_intent_id:
            return None

        return str(inserted_payment_intent_id)
    except Exception as e:
        raise e
