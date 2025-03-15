from typing import Optional, Mapping, Any, List

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import DeleteResult, UpdateResult

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.cart_schema import CartCollectionSchema, CartContentCollectionSchema
from src.models.cart import CartModel
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


def delete_user_cart(user_id: str) -> bool:
    try:
        deleted_cart: DeleteResult = collection.delete_one(
            {"user_id": user_id},
        )

        return deleted_cart.deleted_count > 0
    except Exception as e:
        raise e


def create_user_cart(created_cart: CartCollectionSchema) -> Optional[str]:
    try:
        created_cart['_id'] = ObjectId()

        created_cart_id = collection.insert_one(created_cart).inserted_id

        if not created_cart_id:
            return None

        return str(created_cart_id)
    except Exception as e:
        raise e


def update_user_cart(cart_id: str, updated_cart: CartCollectionSchema) -> bool:
    try:
        updated_cart['_id'] = ObjectId(cart_id)

        updated_cart: UpdateResult = collection.update_one(
            {"_id": ObjectId(cart_id)},
            {"$set": updated_cart}
        )

        return updated_cart.modified_count > 0
    except Exception as e:
        raise e


def add_items_to_user_cart(cart_id: str, new_items: List[CartContentCollectionSchema]) -> bool:
    try:
        updated_cart: UpdateResult = collection.update_one(
            {"_id": ObjectId(cart_id)},
            {"$addToSet": {"cart": {"$each": new_items}}}
        )

        return updated_cart.modified_count > 0
    except Exception as e:
        raise e
