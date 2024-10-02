import logging
from datetime import datetime

import requests
from fastapi import APIRouter
from fastapi_utilities import repeat_every
from pymongo import MongoClient
from starlette import status

from src.database.mongodb.collection.convertion_rates_collection import get_convertion_rates, update_convertion_rates
from src.database.mongodb.schema.convertion_rates_schema import ConvertionRatesCollectionSchema
from src.env_variables.env import env_variables

cron_router = APIRouter(tags=['Auth'])
mongo_client = MongoClient(host=env_variables.mongodb_connection_string)[env_variables.mongodb_database]
currency_convertion_api_url = env_variables.currency_convertion_api_url


@cron_router.on_event('startup')
# @repeat_at(cron='0 * * * *')  # Every hour
@repeat_every(seconds=3600)  # Every hour
def update_db_cached_currencies_convertion_rates():
    logging.info('Executing task to update db cache currencies convertion rates')
    try:
        currencies_convertion_rates = get_convertion_rates()

        if not currencies_convertion_rates:
            return

        for convertion_rate in currencies_convertion_rates:
            now_date = datetime.now()
            convertion_next_date = convertion_rate.nextUpdate

            if convertion_next_date <= now_date:
                convertion = requests.get(
                    url=f'{currency_convertion_api_url}/latest/{convertion_rate.baseCurrency}')

                if convertion.status_code == status.HTTP_200_OK:
                    convertion = convertion.json()

                    convertion = ConvertionRatesCollectionSchema(
                        base_currency=convertion_rate.baseCurrency,
                        last_update=datetime.fromtimestamp(convertion['time_last_update_unix']),
                        next_update=datetime.fromtimestamp(convertion['time_next_update_unix']),
                        convertion_rates=convertion['conversion_rates']
                    )
                    update_convertion_rates(base_currency=convertion_rate.baseCurrency,
                                            convertion_rate_schema=convertion)

    except Exception as ex:
        logging.error(f'Executing task to update db cache currencies convertion rates throw exception -> {ex}')
        raise ex
