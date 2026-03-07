from typing import Optional, Mapping, Any
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.store_schema import StoreCollectionSchema
from src.models.store import StoreModel
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[StoreCollectionSchema] = mongo_client.stores

def get_store_by_id_db(store_id: str) -> Optional[StoreModel]:
    try:
        store = collection.find_one({'_id': ObjectId(store_id)})

        if not store:
            return None

        # Convert _id to id and hex string if needed, 
        # but StoreModel handles ObjectIdTypeConverter
        store['id'] = str(store.pop('_id'))
        
        return StoreModel(**snake_to_camel_case(store))
    except Exception as e:
        raise e
