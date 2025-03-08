from typing import Optional, Mapping, Any, List

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.address_schema import AddressCollectionSchema
from src.database.mongodb.schema.payment_intent_schema import PaymentIntentCollectionSchema
from src.models.address import AddressModel
from src.models.payment_intent import PaymentIntentModel
from src.utils.constants import PaymentIntentStatus
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[AddressCollectionSchema] = mongo_client.addresses


def get_user_address_by_address_id(address_id: str) -> Optional[AddressModel]:
    try:
        address = collection.find_one({'_id': ObjectId(address_id)})

        if not address:
            return None

        return AddressModel(**snake_to_camel_case(address))
    except Exception as e:
        raise e


def get_user_default_address(user_id: str) -> Optional[AddressModel]:
    try:
        address = collection.find_one({'user_id': user_id, 'default': True})

        if not address:
            return None

        return AddressModel(**snake_to_camel_case(address))
    except Exception as e:
        raise e


def get_user_addresses_db(user_id: str) -> Optional[List[AddressModel]]:
    try:
        addresses = collection.find({'user_id': user_id})

        addresses = [AddressModel(**snake_to_camel_case(address)) for address in addresses]

        if len(addresses) <= 0:
            return None

        return addresses
    except Exception as e:
        raise e


def insert_address(inserted_address: AddressCollectionSchema) -> Optional[str]:
    try:
        inserted_address['_id'] = ObjectId()

        inserted_address_id = collection.insert_one(inserted_address).inserted_id

        if not inserted_address_id:
            return None

        return str(inserted_address_id)
    except Exception as e:
        raise e


def delete_address(deleted_address_id: str) -> bool:
    try:
        deleted_address: DeleteResult = collection.delete_one(
            {"_id": ObjectId(deleted_address_id)},
        )

        return deleted_address.deleted_count > 0
    except Exception as e:
        raise e


def update_address_db(address_id: str, updated_address: AddressCollectionSchema) -> bool:
    try:
        updated_address['_id'] = ObjectId(address_id)

        updated_address: UpdateResult = collection.update_one(
            {"_id": ObjectId(address_id)},
            {"$set": updated_address}
        )

        return updated_address.modified_count > 0
    except Exception as e:
        raise e
