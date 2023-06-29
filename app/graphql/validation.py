from typing import Any, Type

from pydantic import BaseModel, ValidationError
import strawberry
from strawberry.extensions import FieldExtension
from strawberry.extensions.field_extension import AsyncExtensionResolver
from strawberry.scalars import JSON
from strawberry.types import Info


@strawberry.type
class ValidationErrorSchema:
    location: list[str]
    message: str
    type: str
    ctx: JSON | None = None


@strawberry.type(name='ValidationError')
class ValidationErrorResponse:
    message: str
    errors: list[ValidationErrorSchema]


class PydanticValidationExtension(FieldExtension):
    def __init__(self, model: Type[BaseModel]):
        self.model = model

    async def resolve_async(self, next_: AsyncExtensionResolver, source: Any, info: Info, **kwargs):
        if 'input_schema' in kwargs:
            try:
                self.model(**strawberry.asdict(kwargs['input_schema']))
            except ValidationError as e:
                return ValidationErrorResponse(
                    message='Validation Error',
                    errors=[
                        ValidationErrorSchema(
                            message=e['msg'], location=list(e['loc']), type=e['type'], ctx=e.get('ctx')
                        )
                        for e in e.errors()
                    ]
                )

        return await next_(source, info, **kwargs)
