import strawberry
from strawberry.types import Info

from app.exceptions import AlreadyExistError, NotFoundError
from app.graphql.authors.responses import (
    AuthorAddResponse,
    AuthorAlreadyExistResponse,
    AuthorGetResponse,
    AuthorNotFoundResponse,
)
from app.graphql.authors.schemas import AuthorCreate
from app.graphql.authors.service import AuthorService
from app.graphql.authors.types import AuthorAddInput, AuthorType
from app.graphql.validation import PydanticValidationExtension


@strawberry.type
class AuthorsQuery:
    @strawberry.field
    async def authors(self, info: Info) -> list[AuthorType]:
        service = AuthorService(settings=info.context['settings'])
        return await service.get_authors()

    @strawberry.field
    async def author(self, author_id: int, info: Info) -> AuthorGetResponse:
        service = AuthorService(settings=info.context['settings'])
        try:
            author = await service.get_author_by_id(author_id)
        except NotFoundError as e:
            return AuthorNotFoundResponse(message=str(e))
        return author


@strawberry.type
class AuthorsMutation:
    @strawberry.mutation(extensions=[PydanticValidationExtension(AuthorCreate)])
    async def create_author(self, input_schema: AuthorAddInput, info: Info) -> AuthorAddResponse:
        service = AuthorService(settings=info.context['settings'])
        try:
            author = await service.create_author(name=input_schema.name)
        except AlreadyExistError as e:
            return AuthorAlreadyExistResponse(message=str(e))
        return author

    @strawberry.mutation
    async def delete_author(self, author_id: int, info: Info) -> None | AuthorNotFoundResponse:
        service = AuthorService(settings=info.context['settings'])
        try:
            await service.delete_author(author_id)
        except NotFoundError as e:
            return AuthorNotFoundResponse(message=str(e))
        return None
