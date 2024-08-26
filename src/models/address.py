from typing import Optional

from pydantic import Field

from src.shared.generics import CommonModel


class AddressModel(CommonModel):
    id: Optional[str] = None
    userId: Optional[str] = None
    country: str = Field(min_length=1)
    countryCode: str = Field(min_length=1)
    state: str = Field(min_length=1)
    stateCode: str = Field(min_length=1)
    city: str = Field(min_length=1)
    postalCode: str = Field(min_length=1)
    address: str = Field(min_length=1)
    additionalAddress: Optional[str] = None
    default: bool = Field(default=True)

    model_config = dict(
        json_schema_extra=dict(
            example=dict(
                country="United States",
                state="New York",
                city="Brooklyn",
                postalCode=123454,
                address="Lorem ipsum",
                default="False"
            )
        )
    )

    @staticmethod
    def to_model(address: dict):
        return AddressModel(
            id=str(address['_id']),
            userId=str(address['user_id']),
            country=address['country'],
            state=address['state'],
            city=address['city'],
            postalCode=address['postal_code'],
            address=address['address'],
            default=address['default'],
            additionalAddress=address.get('additional_address')
        )
