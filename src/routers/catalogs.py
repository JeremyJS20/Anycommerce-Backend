from typing import List

import requests
from fastapi import APIRouter, Depends, Path
from fastapi import status

from dependencies.auth import validate_api_key
from src.env_variables.env import env_variables
from src.models.responses.catalogs import CountriesResponse, StatesResponse, CitiesResponse
from src.shared.exceptions import HttpException
from src.shared.generics import Data

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
