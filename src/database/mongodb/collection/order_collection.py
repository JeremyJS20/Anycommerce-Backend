from typing import Optional, Mapping, Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.order_schema import OrderCollectionSchema

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[OrderCollectionSchema] = mongo_client.orders


def insert_order(inserted_order: OrderCollectionSchema) -> Optional[str]:
    try:
        inserted_order['_id'] = ObjectId()

        inserted_order_id = collection.insert_one(inserted_order).inserted_id

        if not inserted_order_id:
            return None

        return str(inserted_order_id)
    except Exception as e:
        raise e

# def get_user_address_by_address_id(address_id: str) -> Optional[AddressModel]:
#     try:
#         address = collection.find_one({'_id': ObjectId(address_id)})
#
#         if not address:
#             return None
#
#         return AddressModel(**snake_to_camel_case(address))
#     except Exception as e:
#         raise e
#
#
# def get_user_default_address(user_id: str) -> Optional[AddressModel]:
#     try:
#         address = collection.find_one({'user_id': user_id, 'default': True})
#
#         if not address:
#             return None
#
#         return AddressModel(**snake_to_camel_case(address))
#     except Exception as e:
#         raise e
#
#
# def get_user_addresses_db(user_id: str) -> Optional[List[AddressModel]]:
#     try:
#         addresses = collection.find({'user_id': user_id})
#
#         addresses = [AddressModel(**snake_to_camel_case(address)) for address in addresses]
#
#         if len(addresses) <= 0:
#             return None
#
#         return addresses
#     except Exception as e:
#         raise e
#
#
# def delete_address(deleted_address_id: str) -> bool:
#     try:
#         deleted_address: DeleteResult = collection.delete_one(
#             {"_id": ObjectId(deleted_address_id)},
#         )
#
#         return deleted_address.deleted_count > 0
#     except Exception as e:
#         raise e
#
#
# def update_address_db(address_id: str, updated_address: AddressCollectionSchema) -> bool:
#     try:
#         updated_address['_id'] = ObjectId(address_id)
#
#         updated_address: UpdateResult = collection.update_one(
#             {"_id": ObjectId(address_id)},
#             {"$set": updated_address}
#         )
#
#         return updated_address.modified_count > 0
#     except Exception as e:
#         raise e
