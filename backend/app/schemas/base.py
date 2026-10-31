from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """
    Base model that converts snake_case Python attributes to camelCase
    in JSON serialization, exactly matching the frontend TypeScript contracts.
    Accepts both camelCase and snake_case during parsing/validation.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
