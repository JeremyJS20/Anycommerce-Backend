from typing import Optional, Mapping, Any

from pymongo.collection import Collection
from pymongo.database import Database

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.user_schema import UserCollectionSchema
from src.models.user import UserModel
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[UserCollectionSchema] = mongo_client.user


def get_user_by_email(email: str) -> Optional[UserModel]:
    try:
        user_schema = collection.find_one({'email.value': email})

        if not user_schema:
            return None

        return UserModel(**snake_to_camel_case(user_schema))
    except Exception as e:
        raise e


def insert_user(new_user: UserCollectionSchema) -> Optional[str]:
    try:
        inserted_user_id = collection.insert_one(new_user).inserted_id

        if not inserted_user_id:
            return None

        return str(inserted_user_id)
    except Exception as e:
        raise e
