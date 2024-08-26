from pydantic import BaseModel


class EmailModel(BaseModel):
    value: str
    verified: bool

    model_config = dict(
        json_schema_extra=dict(
            example=dict(
                value="example@example.com",
                verified=False
            )
        )
    )
