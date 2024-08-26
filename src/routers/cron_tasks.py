import logging
from datetime import datetime

import requests
from fastapi import APIRouter
from fastapi_utilities import repeat_at, repeat_every
from pymongo import MongoClient
from starlette import status

from src.env_variables.env import env_variables
from src.models.currency_api import CurrencyConvertionRatesModel

cron_router = APIRouter(tags=['Auth'])
mongo_client = MongoClient(host=env_variables.mongodb_connection_string)[env_variables.mongodb_database]
currency_convertion_api_url = env_variables.currency_convertion_api_url


@cron_router.on_event('startup')
# @repeat_at(cron='0 * * * *')  # Every hour
@repeat_every(seconds=3600)  # Every hour
def update_db_cached_currencies_convertion_rates():
    logging.info('Executing task to update db cache currencies convertion rates')
    try:
        currencies_convertion_rates_db = mongo_client.convertion_rates.find()

        currencies_convertion_rates = [CurrencyConvertionRatesModel(
            baseCurrency=currency['base_currency'],
            lastUpdate=currency['last_update'],
            nextUpdate=currency['next_update'],
            convertionRates=currency['convertion_rates']
        ) for currency in currencies_convertion_rates_db]

        if len(currencies_convertion_rates) <= 0:
            return

        for convertion_rate in currencies_convertion_rates:
            now_date = datetime.now()
            convertion_next_date = convertion_rate.nextUpdate

            if convertion_next_date <= now_date:
                convertion = requests.get(
                    url=f'{currency_convertion_api_url}/latest/{convertion_rate.baseCurrency}')

                if convertion.status_code == status.HTTP_200_OK:
                    convertion = convertion.json()

                    convertion = dict(
                        base_currency=convertion_rate.baseCurrency,
                        last_update=datetime.fromtimestamp(convertion['time_last_update_unix']),
                        next_update=datetime.fromtimestamp(convertion['time_next_update_unix']),
                        convertion_rates=convertion['conversion_rates']
                    )

                    mongo_client.convertion_rates.update_one(
                        {"base_currency": convertion_rate.baseCurrency},
                        {"$set": convertion}
                    )

    except Exception as ex:
        logging.error(f'Executing task to update db cache currencies convertion rates throw exception -> {ex}')
        raise ex
