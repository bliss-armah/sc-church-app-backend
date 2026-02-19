from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """
    Base model for all API schemas.

    - **Responses** are serialized with camelCase field names (alias_generator).
    - **Requests** accept both camelCase and snake_case  (populate_by_name=True),
      so the frontend can send camelCase while Python internals use snake_case.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,   # accept snake_case input too
        from_attributes=True,    # allows ORM mode (replaces orm_mode in Pydantic v1)
    )
