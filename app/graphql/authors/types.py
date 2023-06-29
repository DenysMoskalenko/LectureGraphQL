from typing import Annotated, TYPE_CHECKING

import strawberry
from strawberry.types import Info

if TYPE_CHECKING:
    from app.graphql.books.types import BookType


@strawberry.input(name='AuthorAdd')
class AuthorAddInput:
    name: str


@strawberry.input(name='AuthorUpdate')
class AuthorUpdateInput(AuthorAddInput):
    pass


@strawberry.type(name='Author')
class AuthorType:
    id: int
    name: str

    @strawberry.field
    async def books(self, info: Info) -> list[Annotated['BookType', strawberry.lazy('app.graphql.books.types')]]:
        from app.graphql.books.service import BookService

        service = BookService(settings=info.context['settings'])
        return await service.get_books_by_author_id(self.id)
