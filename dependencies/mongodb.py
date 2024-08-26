from pymongo import MongoClient

from src.env_variables.env import env_variables


class MongoDBClient:
    _mongo_instance: MongoClient = None

    def __init__(self):
        if self._mongo_instance is None:
            self._mongo_instance = MongoClient(host=env_variables.mongodb_connection_string)

    def __call__(self):
        return self._mongo_instance[env_variables.mongodb_database]
