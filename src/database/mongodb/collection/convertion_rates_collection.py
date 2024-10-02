from typing import Optional, Mapping, Any, List

from pymongo.collection import Collection
from pymongo.database import Database

from dependencies.mongodb import MongoDBClient
from src.database.mongodb.schema.convertion_rates_schema import ConvertionRatesCollectionSchema
from src.database.mongodb.schema.user_preferences_schema import UserPreferencesCollectionSchema
from src.database.mongodb.schema.user_schema import UserCollectionSchema
from src.models.currency_api import CurrencyConvertionRatesModel
from src.models.user import UserModel, UserPreferencesModel
from src.utils.utils import snake_to_camel_case

mongo_client: Database[Mapping[str, Any] | Any] = MongoDBClient()()
collection: Collection[ConvertionRatesCollectionSchema] = mongo_client.convertion_rates


def get_convertion_rates() -> Optional[List[CurrencyConvertionRatesModel]]:
    try:
        convertion_rates = collection.find()

        convertion_rates = [CurrencyConvertionRatesModel(**snake_to_camel_case(convertion_rate)) for convertion_rate in
                            convertion_rates]

        if not convertion_rates:
            return None

        return convertion_rates
    except Exception as e:
        raise e


def get_convertion_rate_by_base_currency(base_currency: str) -> Optional[CurrencyConvertionRatesModel]:
    try:
        convertion_rate = collection.find_one({'base_currency': base_currency})

        if not convertion_rate:
            return None

        return CurrencyConvertionRatesModel(**snake_to_camel_case(convertion_rate))
    except Exception as e:
        raise e


def insert_convertion_rate(convertion_rate_schema: ConvertionRatesCollectionSchema) -> Optional[str]:
    try:
        inserted_convertion_rate_id = collection.insert_one(convertion_rate_schema).inserted_id

        if not inserted_convertion_rate_id:
            return None

        return str(inserted_convertion_rate_id)
    except Exception as e:
        raise e


def update_convertion_rates(base_currency: str, convertion_rate_schema: ConvertionRatesCollectionSchema) -> Optional[
    str]:
    try:
        updated_convertion_rate_id = collection.update_one(
            {"base_currency": base_currency},
            {"$set": convertion_rate_schema}
        ).upserted_id

        if not updated_convertion_rate_id:
            return None

        return str(updated_convertion_rate_id)
    except Exception as e:
        raise e
