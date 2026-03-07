from typing import Any, Optional

from pydantic import Field

from src.shared.generics import CommonModel


class CommonType(CommonModel):
    key: str = Field(min_length=1)
    text: str = Field(min_length=1)
    value: Any
    description: Optional[str] = None
    icon: Optional[str] = None


class MediaModel(CommonModel):
    name: str = Field(default='default')
    size: float = Field(default=5)
    extension: str = Field(default='.jpeg')
    url: str = Field(default='https://www.brandi.com.ar/wp-content/uploads/2020/08/a-no-foto.png')


class FeatureModel(CommonModel):
    key: str = Field(min_length=1)
    label: str = Field(min_length=1)
    icon: str = Field(min_length=1)
    details: str = Field(min_length=1)


