from typing import Optional, Union, Literal, List

from pydantic import BaseModel

from src.models.submodels.email import EmailModel
from src.models.submodels.phone import PhoneModel
from src.shared.generics import CommonModel
from src.utils.utils import camel_to_snake_case, ObjectIdTypeConverter


class CategoriesModel(CommonModel):
    id: ObjectIdTypeConverter
    name: str
    description: str
    subcategories: List[str]
