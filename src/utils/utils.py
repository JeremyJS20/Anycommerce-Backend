import math
from datetime import datetime
from typing import Mapping, Any

import requests
from bson import ObjectId as BaseObjectId
from bson.errors import InvalidId
from pymongo.database import Database
from starlette import status

from src.env_variables.env import env_variables
from src.utils.constants import DateFormats

currency_convertion_api_url = env_variables.currency_convertion_api_url


def camel_to_snake_case(input_dict):
    def convert_keys(d):
        if isinstance(d, dict):
            snake_dict = {}
            for key, value in d.items():
                snake_case_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key])

                if snake_case_key == "id":
                    snake_case_key = "_" + snake_case_key

                snake_dict[snake_case_key] = convert_keys(value)
            return snake_dict
        elif isinstance(d, list):
            return [convert_keys(item) for item in d]
        else:
            return d

    return convert_keys(input_dict)


def snake_to_camel_case(input_dict):
    def convert_keys(d):
        if isinstance(d, dict):
            camel_dict = {}
            for key, value in d.items():
                components = key.split('_')
                camel_case_key = components[0] + ''.join(x.capitalize() for x in components[1:]) if components[
                                                                                                        0] != '' else \
                    components[1]
                camel_dict[camel_case_key] = convert_keys(value)
            return camel_dict
        elif isinstance(d, list):
            return [convert_keys(item) for item in d]
        else:
            return d

    return convert_keys(input_dict)


def validate_date(date: str, format: DateFormats = DateFormats.DATE_YYYY_MM_DD):
    try:
        datetime.strptime(date, str(format))
        return True
    except ValueError:
        return False


def convert_currency(base_currency: str, target_currency: str, amount: float,
                     mongo_client: Database[Mapping[str, Any]]):
    if base_currency != target_currency:
        currency_convertion_rate_db = mongo_client.convertion_rates.find_one({'base_currency': base_currency})

        if currency_convertion_rate_db:
            amount = convert_currency_2(
                target_convertion_rate=currency_convertion_rate_db['convertion_rates'][target_currency],
                amount=amount)
        else:
            convertion = requests.get(
                url=f'{currency_convertion_api_url}/latest/{base_currency}')

            if convertion.status_code == status.HTTP_200_OK:
                convertion = convertion.json()

                convertion = dict(
                    base_currency=base_currency,
                    last_update=datetime.fromtimestamp(convertion['time_last_update_unix']),
                    next_update=datetime.fromtimestamp(convertion['time_next_update_unix']),
                    convertion_rates=convertion['conversion_rates']
                )

                mongo_client.convertion_rates.insert_one(convertion)
                amount = convert_currency_2(
                    target_convertion_rate=convertion['convertion_rates'][target_currency],
                    amount=amount)

    return int(math.ceil(amount))


def convert_currency_2(target_convertion_rate: float, amount: float):
    return amount * target_convertion_rate


class ObjectIdTypeConverter(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: Any
    ) -> Any:
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.any_schema()
        )

    @classmethod
    def validate(cls, value: Any) -> str:
        if isinstance(value, BaseObjectId):
            return str(value)
        if isinstance(value, str) and BaseObjectId.is_valid(value):
            return value
        raise ValueError("Not a valid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(
            cls, core_schema: Any, handler: Any
    ) -> Any:
        # For JSON schema, we want this to be represented as a string
        return handler.resolve_ref_schema(handler(core_schema)) | {'type': 'string'}
