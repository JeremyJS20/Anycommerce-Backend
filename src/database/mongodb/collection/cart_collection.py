from typing import Optional, Mapping, Any

from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import DeleteResult

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.cart_schema import CartCollectionSchema
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
