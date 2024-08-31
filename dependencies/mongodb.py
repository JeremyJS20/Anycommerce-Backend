from typing import Any, Mapping

from pymongo import MongoClient
from pymongo.database import Database

from src.env_variables.env import env_variables


class MongoDBClient:
    _mongo_instance: MongoClient = None

    def __init__(self, connection_string: str = None, database_name: str = None):
        if not MongoDBClient._mongo_instance:
            try:
                connection_string = connection_string or env_variables.mongodb_connection_string
                MongoDBClient._mongo_instance = MongoClient(host=connection_string)
            except ConnectionError as e:
                raise Exception(f"Failed to connect to MongoDB: {e}")

        self.database_name = database_name or env_variables.mongodb_database

        if not self.database_name:
            raise ValueError("Database name must be provided.")

        self._database = MongoDBClient._mongo_instance[self.database_name]

    def __call__(self) -> Database[Mapping[str, Any] | Any]:
        return self._database
