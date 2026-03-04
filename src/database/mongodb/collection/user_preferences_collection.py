from typing import Optional, Mapping, Any
from bson import ObjectId

from pymongo.collection import Collection
from pymongo.database import Database

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.user_preferences_schema import UserPreferencesCollectionSchema
from src.database.mongodb.schema.user_schema import UserCollectionSchema
from src.models.user import UserModel, UserPreferencesModel
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[UserPreferencesCollectionSchema] = mongo_client.preferences


def get_user_preferences_by_id(user_id: str) -> Optional[UserPreferencesModel]:
    try:
        user_preferences_schema = collection.find_one({'user_id': user_id})

        if not user_preferences_schema:
            return None

        return UserPreferencesModel(**snake_to_camel_case(user_preferences_schema)['preferences'])
    except Exception as e:
        raise e


def insert_user_preferences(preferences: UserPreferencesCollectionSchema) -> Optional[str]:
    try:
        preferences['_id'] = ObjectId()

        inserted_id = collection.insert_one(preferences).inserted_id

        if not inserted_id:
            return None

        return str(inserted_id)
    except Exception as e:
        raise e