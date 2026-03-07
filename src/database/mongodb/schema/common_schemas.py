from typing import TypedDict, Optional, Any


class CommonTypeSchema(TypedDict):
    key: str
    text: str
    value: Any
    description: Optional[str]
    icon: Optional[str]


class MediaSchema(TypedDict):
    name: str
    size: float
    extension: str
    url: str


class AttributeTypeSchema(TypedDict):
    key: str
    value: Any
    price: Optional[int]
    available: bool
    default: bool


class FeatureSchema(TypedDict):
    key: str
    label: str
    icon: str
    details: str
