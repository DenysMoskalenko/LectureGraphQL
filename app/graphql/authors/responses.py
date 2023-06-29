import strawberry

from app.graphql.authors.types import AuthorType
from app.graphql.validation import ValidationErrorResponse


@strawberry.type(name='AuthorNotFound')
class AuthorNotFoundResponse:
    message: str = 'Requested Author not found'


@strawberry.type(name='AuthorAlreadyExist')
class AuthorAlreadyExistResponse:
    message: str = 'Author already exist'


AuthorGetResponse = strawberry.union('AuthorGetResponse', (AuthorType, AuthorNotFoundResponse))
AuthorAddResponse = strawberry.union(
    'AuthorAddResponse', (AuthorType, ValidationErrorResponse, AuthorAlreadyExistResponse)
)
AuthorUpdateResponse = strawberry.union(
    'AuthorUpdateResponse', (AuthorType, ValidationErrorResponse, AuthorNotFoundResponse, AuthorAlreadyExistResponse)
)
