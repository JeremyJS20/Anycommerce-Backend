from typing import Optional, Mapping, Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.session_token_schema import SessionTokenCollectionSchema
from src.models.session_token import SessionTokenModel
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[SessionTokenCollectionSchema] = mongo_client.session_token


def get_session_token(refresh_token: Optional[str] = None, username: Optional[str] = None,
                      access_token: Optional[str] = None) -> (
        Optional)[SessionTokenModel]:
    try:
        session_token = None

        if refresh_token:
            session_token = collection.find_one({'data.refresh_token': refresh_token})
        elif username:
            session_token = collection.find_one({'username': username})
        elif access_token:
            session_token = collection.find_one({'data.access_token': access_token})

        if not session_token:
            return None

        return SessionTokenModel(**snake_to_camel_case(session_token))
    except Exception as e:
        raise e


def insert_session_token(session_token: SessionTokenCollectionSchema) -> Optional[str]:
    try:
        inserted_session_token_id = collection.insert_one(session_token).inserted_id

        if not inserted_session_token_id:
            return None

        return str(inserted_session_token_id)
    except Exception as e:
        raise e


def update_session_token_with_id(token_id: str, session_token: SessionTokenCollectionSchema) -> Optional[str]:
    try:
        updated_session_token_id = collection.update_one(
            {"_id": ObjectId(token_id)},
            {"$set": session_token}
        ).upserted_id

        if not updated_session_token_id:
            return None

        return str(updated_session_token_id)
    except Exception as e:
        raise e


def remove_session_token(refresh_token: Optional[str] = None,
                         username: Optional[str] = None) -> bool:
    try:
        if refresh_token:
            collection.delete_one({'data.refresh_token': refresh_token})
        elif username:
            collection.delete_one({'username': username})

        return True
    except Exception as e:
        raise e


def remove_many_sessions_token(refresh_token: Optional[str] = None,
                               username: Optional[str] = None) -> bool:
    try:
        if refresh_token:
            collection.delete_many({'data.refresh_token': refresh_token})
        elif username:
            collection.delete_many({'username': username})

        return True
    except Exception as e:
        raise e
