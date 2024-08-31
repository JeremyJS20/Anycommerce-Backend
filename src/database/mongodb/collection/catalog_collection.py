from typing import Optional, Mapping, Any, List

from pymongo.collection import Collection
from pymongo.database import Database

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.catalog_schema import CategoryCatalogCollectionSchema
from src.models.catalog import CategoriesModel
from src.models.user import UserModel
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[CategoryCatalogCollectionSchema] = mongo_client.categories


def get_categories() -> Optional[List[CategoriesModel]]:
    try:
        categories = collection.find()

        categories = [CategoriesModel(**snake_to_camel_case(category)) for category in categories]

        if len(categories) <= 0:
            return None

        return categories
    except Exception as e:
        raise e
