import strawberry

from app.graphql.books.types import BookType
from app.graphql.validation import ValidationErrorResponse


@strawberry.type(name='BookNotFound')
class BookNotFoundResponse:
    message: str = 'Requested Book not found'


@strawberry.type(name='BookAlreadyExist')
class BookAlreadyExistResponse:
    message: str = 'Book already exist'


BookGetResponse = strawberry.union('BookGetResponse', (BookType, BookNotFoundResponse))
BookAddResponse = strawberry.union(
    'BookAddResponse', (BookType, ValidationErrorResponse, BookAlreadyExistResponse)
)
BookUpdateResponse = strawberry.union(
    'BookUpdateResponse', (BookType, ValidationErrorResponse, BookNotFoundResponse, BookAlreadyExistResponse)
)
