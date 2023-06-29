import strawberry
from strawberry.types import Info

from app.exceptions import AlreadyExistError, NotFoundError
from app.graphql.authors.responses import AuthorNotFoundResponse
from app.graphql.books.responses import BookAddResponse, BookAlreadyExistResponse, BookGetResponse, BookNotFoundResponse
from app.graphql.books.schemas import BookCreate
from app.graphql.books.service import BookService
from app.graphql.books.types import BookAddInput, BookType
from app.graphql.validation import PydanticValidationExtension


@strawberry.type
class BooksQuery:
    @strawberry.field
    async def books(self, info: Info) -> list[BookType]:
        service = BookService(settings=info.context['settings'])
        return await service.get_books()

    @strawberry.field
    async def book(self, book_id: int, info: Info) -> BookGetResponse:
        service = BookService(settings=info.context['settings'])
        try:
            book = await service.get_book_by_id(book_id)
        except NotFoundError as e:
            return BookNotFoundResponse(message=str(e))
        return book


@strawberry.type
class BooksMutation:
    @strawberry.mutation(extensions=[PydanticValidationExtension(BookCreate)])
    async def create_book(self, input_schema: BookAddInput, info: Info) -> BookAddResponse:
        service = BookService(settings=info.context['settings'])
        try:
            book = await service.create_book(author_id=input_schema.author_id, name=input_schema.name)
        except NotFoundError as e:
            return AuthorNotFoundResponse(message=(str(e)))
        except AlreadyExistError as e:
            return BookAlreadyExistResponse(message=str(e))
        return book

    @strawberry.mutation
    async def delete_book(self, book_id: int, info: Info) -> None | BookNotFoundResponse:
        service = BookService(settings=info.context['settings'])
        try:
            await service.delete_book(book_id)
        except NotFoundError as e:
            return BookNotFoundResponse(message=str(e))
        return None
