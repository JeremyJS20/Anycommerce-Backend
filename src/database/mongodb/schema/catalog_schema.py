from datetime import datetime
from typing import TypedDict, NotRequired, List

from bson import ObjectId


class CategoryCatalogCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    name: str
    description: str
    subcategories: List[str]
