from datetime import datetime
from typing import Optional, Any, List

from pydantic import Field, Extra

from src.models.common import MediaModel, CommonType
from src.shared.generics import CommonModel


class AttributeType(CommonModel):
    key: str = Field(min_length=1)
    value: Any
    price: Optional[int] = None
    available: bool = Field(default=False)
    default: bool = Field(default=False)


class ProductDetails(CommonModel):
    description: str = Field(min_length=1)
    characteristics: Optional[List[CommonType]] = None


class ProductDates(CommonModel):
    creation: datetime
    restock: datetime


class ProductVariants(CommonModel):
    colors: Optional[List[AttributeType]] = None
    sizes: Optional[List[AttributeType]] = None
    # extra: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "extra": Extra.allow
    }

    # def __init__(self, **data):
    #     extra_data = {k: v for k, v in data.items() if k not in self.__fields__}
    #     super().__init__(**data)
    #     self.extra.update(extra_data)


class ProductModel(CommonModel):
    id: Optional[str] = None
    storeId: Optional[str] = None
    name: str = Field(min_length=1)
    cost: float = Field(gt=0)
    currency: str = Field(min_length=1)
    stock: int = Field(gt=0)
    category: str = Field(min_length=1)
    subcategory: str = Field(min_length=1)
    rating: Optional[float] = None
    imgs: Optional[List[MediaModel]] = Field(default=[MediaModel().to_json()])
    dates: ProductDates
    details: ProductDetails
    variants: ProductVariants

    model_config = dict(
        json_schema_extra=dict(
            example=dict(
                storeId="662e9cdce7bd223fe6b10aa8",
                name='Lenovo Legion 5 Ryzen 5 RTX 3060',
                cost=1100,
                currency="USD",
                stock=10,
                category="Electronics",
                subcategory="Laptops",
                dates=dict(
                    creation=datetime.now(),
                    restock=datetime.now()
                ),
                details=dict(
                    description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
                ),
                rating=5.0,
                attributes=dict(
                    color='#000000',
                    size=dict(
                        unit='cm',
                        value=5.5
                    ),
                    weight=dict(
                        unit='lb',
                        value=5.5
                    )
                ),
                imgs=[
                    dict(
                        name="random.jpeg",
                        size=5.0,
                        extension=".jpeg",
                        url="https://picsum.photos/id/96/200/300"
                    ),
                    dict(
                        name="random2.jpeg",
                        size=5.0,
                        extension=".jpeg",
                        url="https://picsum.photos/id/96/200/300"
                    )
                ]
            )
        )
    )

    @staticmethod
    def to_model(product: dict):
        return ProductModel(
            id=str(product.get('_id') or product.get('id')),
            storeId=str(product['store_id']),
            name=product['name'],
            cost=product['cost'],
            currency=product['currency'],
            stock=product['stock'],
            category=product['category'],
            subcategory=product['subcategory'],
            dates=product['dates'],
            details=product['details'],
            variants=product['variants'],
            rating=product.get('rating'),
            imgs=product.get('imgs'),
        )
