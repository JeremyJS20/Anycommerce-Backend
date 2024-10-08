from typing import List, Mapping, Any

import requests
from fastapi import APIRouter, Depends, Path
from fastapi import status
from pymongo.database import Database

from dependencies.auth import validate_api_key
from dependencies.mongodb import MongoDBClient
from src.database.mongodb.collection.catalog_collection import get_categories
from src.env_variables.env import env_variables
from src.models.responses.catalogs import CountriesResponse, StatesResponse, CitiesResponse, CategoriesResponse
from src.shared.exceptions import HttpException
from src.shared.generics import Data, ErrorResponse
from src.utils.constants import ErrorsIDs, ErrorsDescriptionsObject

catalogs_router = APIRouter(tags=['Catalogs'])
countries_api_url = env_variables.countries_api_url
countries_api_key = env_variables.countries_api_key


@catalogs_router.get('/countries', responses={
    status.HTTP_200_OK: {"model": Data[List[CountriesResponse]], 'description': 'Countries found'},
}, status_code=status.HTTP_200_OK)
def get_countries(
        _: str = Depends(validate_api_key),
):
    try:
        countries = requests.get(f'{countries_api_url}/countries', headers={
            "X-CSCAPI-KEY": countries_api_key
        })

        countries = [CountriesResponse(
            id=str(country['id']),
            name=country['name'],
            countryCode=country['iso2'],
            phoneCode=str(country['phonecode']).split(' and '),
            currency=country['currency'],
            emoji=country['emoji']
        ) for country in countries.json()]

        return Data[List[CountriesResponse]](
            data=countries
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@catalogs_router.get('/countries/{countryCode}/states', responses={
    status.HTTP_200_OK: {"model": Data[List[StatesResponse]], 'description': 'States found'},
}, status_code=status.HTTP_200_OK)
def get_country_states(
        _: str = Depends(validate_api_key),
        country_code: str = Path(alias='countryCode', min_length=1)
):
    try:
        states = requests.get(f'{countries_api_url}/countries/{country_code}/states', headers={
            "X-CSCAPI-KEY": countries_api_key
        })

        states = [StatesResponse(
            id=str(state['id']),
            name=state['name'],
            stateCode=state['iso2'],
        ) for state in states.json()]

        return Data[List[StatesResponse]](
            data=states
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@catalogs_router.get('/countries/{countryCode}/states/{stateCode}/cities', responses={
    status.HTTP_200_OK: {"model": Data[List[CitiesResponse]], 'description': 'Cities found'},
}, status_code=status.HTTP_200_OK)
def get_country_state_cities(
        _: str = Depends(validate_api_key),
        country_code: str = Path(alias='countryCode', min_length=1),
        state_code: str = Path(alias='stateCode', min_length=1)
):
    try:
        cities = requests.get(f'{countries_api_url}/countries/{country_code}/states/{state_code}/cities', headers={
            "X-CSCAPI-KEY": countries_api_key
        })

        cities = [CitiesResponse(
            id=str(city['id']),
            name=city['name']
        ) for city in cities.json()]

        return Data[List[CitiesResponse]](
            data=cities
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@catalogs_router.get('/categories', responses={
    status.HTTP_200_OK: {"model": Data[List[CategoriesResponse]], 'description': 'Categories found'},
    status.HTTP_404_NOT_FOUND: {"model": Data[ErrorResponse], 'description': 'Categories not found'},
}, status_code=status.HTTP_200_OK)
def get_product_categories(
        _: str = Depends(validate_api_key)
):
    try:
        categories = get_categories()

        if not categories:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptionsObject[ErrorsIDs.NO_RECORDS_FOUND].format('categories')
            )

        categories = [CategoriesResponse(**category.to_json()) for category in categories]

        return Data[List[CategoriesResponse]](data=categories)

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex
