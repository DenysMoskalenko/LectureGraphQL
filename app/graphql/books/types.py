from typing import Annotated, TYPE_CHECKING

import strawberry
from strawberry.types import Info

if TYPE_CHECKING:
    from app.graphql.authors.types import AuthorType


@strawberry.input
class BookAddInput:
    name: str
    author_id: int


@strawberry.input
class BookUpdateInput(BookAddInput):
    pass


@strawberry.type(name='Book')
class BookType:
    id: int
    name: str = None
    author_id: int = None

    @strawberry.field
    async def author(self, info: Info) -> Annotated['AuthorType', strawberry.lazy('app.graphql.authors.types')]:
        from app.graphql.authors.service import AuthorService

        service = AuthorService(settings=info.context['settings'])
        return await service.get_author_by_id(self.author_id)
