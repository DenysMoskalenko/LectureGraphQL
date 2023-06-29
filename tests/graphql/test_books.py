from app.graphql.books.service import BookService
from app.graphql.books.types import BookType
from tests.factories import BookFactory


async def create_test_book(author_id: int, *, name: str | None = None) -> BookType:
    from app.core.config import get_settings

    book_factory = BookFactory(author_id=author_id, name=name) if name is not None else BookFactory(author_id=author_id)

    service = BookService(settings=get_settings())
    return await service.create_book(author_id=author_id, name=book_factory.name)
