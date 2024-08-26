from pydantic import BaseModel


class PhoneModel(BaseModel):
    country: str
    prefix: str
    value: str
    verified: bool

    model_config = dict(
        json_schema_extra=dict(
            example=dict(
                countryAlpha2="DO",
                prefix="+1 809",
                value="1234456",
                verified=False
            )
        )
    )
