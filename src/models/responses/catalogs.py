from datetime import datetime
from typing import List

from src.shared.generics import CommonModel


class CountriesResponse(CommonModel):
    id: str
    name: str
    countryCode: str
    phoneCode: List[str]
    currency: str
    emoji: str


class StatesResponse(CommonModel):
    id: str
    name: str
    stateCode: str


class CitiesResponse(CommonModel):
    id: str
    name: str


class CategoriesResponse(CommonModel):
    id: str
    name: str
    description: str
    subcategories: List[str]
