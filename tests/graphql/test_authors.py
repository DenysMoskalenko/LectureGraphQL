import pytest

from app.graphql.authors.service import AuthorService
from app.graphql.authors.types import AuthorAddInput, AuthorType
from app.graphql.converters import strawberry_to_dict
from tests.conftest import TestBaseClientDBClass
from tests.factories import AuthorFactory
from tests.graphql.test_books import create_test_book


async def create_test_author(*, name: str | None = None) -> AuthorType:
    from app.core.config import get_settings

    author_factory = AuthorFactory(name=name) if name is not None else AuthorFactory()

    service = AuthorService(settings=get_settings())
    return await service.create_author(name=author_factory.name)


class TestAuthorList(TestBaseClientDBClass):
    QUERY = """
        query TestQuery {
            authors {
                id
            }
        }
    """

    async def test_get_empty(self):
        response = await self.client.post('/graphql', json={'query': self.QUERY})

        response_data = response.json()['data']['authors']
        assert response_data == []

    async def test_list(self):
        author1, author2 = await create_test_author(), await create_test_author()

        response = await self.client.post('/graphql', json={'query': self.QUERY})

        response_data = response.json()['data']['authors']
        assert response_data == [
            {'id': author1.id},
            {'id': author2.id},
        ]


class TestAuthorGet(TestBaseClientDBClass):
    QUERY = """
        query TestQuery($author_id: Int!) {
            author(author_id: $author_id) {
                ... on Author {
                    id
                    name
                    books {
                        id
                        author_id
                        name
                    }
                }
                ... on AuthorNotFound {
                    message
                }
            }
        }
    """

    async def test_get(self):
        author = await create_test_author()

        response = await self.client.post(
            '/graphql', json={'query': self.QUERY, 'variables': {'author_id': author.id}}
        )

        response_data = response.json()['data']['author']
        assert response_data == strawberry_to_dict(author, exclude={'books'}) | {'books': []}

    async def test_get_with_books(self):
        author = await create_test_author()
        book1, book2 = await create_test_book(author.id), await create_test_book(author.id)

        response = await self.client.post(
            '/graphql', json={'query': self.QUERY, 'variables': {'author_id': author.id}}
        )

        response_data = response.json()['data']['author']
        assert response_data == {
            **strawberry_to_dict(author, exclude={'books'}),
            'books': [strawberry_to_dict(b, exclude={'author'}) for b in (book1, book2)],
        }

    async def test_not_found(self):
        unreal_id = -99999999

        response = await self.client.post(
            '/graphql', json={'query': self.QUERY, 'variables': {'author_id': unreal_id}}
        )

        response_data = response.json()['data']['author']
        assert response_data == {'message': f'Author(id={unreal_id}) Not Found'}


class TestAuthorCreate(TestBaseClientDBClass):
    MUTATION = """
        mutation TestMutation($name: String!) {
            create_author(input_schema: {name: $name}) {
                ... on Author {
                    id
                    name
                }
                ... on ValidationError {
                    message
                }
                ... on AuthorAlreadyExist {
                    message
                }
            }
        }
    """

    async def test_create(self):
        author_factory = AuthorFactory()

        response = await self.client.post(
            '/graphql', json={'query': self.MUTATION, 'variables': author_factory.variables()}
        )

        response_data = response.json()['data']['create_author']
        assert response_data['name'] == author_factory.name

    async def test_create_not_unique(self):
        author_factory = AuthorFactory()
        exist_author = await create_test_author()

        response = await self.client.post(
            '/graphql',
            json={
                'query': self.MUTATION,
                'variables': {**author_factory.variables(), 'name': exist_author.name},
            },
        )

        assert response.json()['data']['create_author'] == {'message': 'Author with this name already exist'}

    @pytest.mark.parametrize(
        'author_input', [
            AuthorAddInput(name='', ),
            AuthorAddInput(name='very_long' * 10),
            AuthorAddInput(name='Adolf Hitler'),
        ]
    )
    async def test_create_invalid_data(self, author_input: AuthorAddInput):
        response = await self.client.post(
            '/graphql',
            json={'query': self.MUTATION, 'variables': strawberry_to_dict(author_input)},
        )
        assert response.json()['data']['create_author'] == {'message': 'Validation Error'}


class TestAuthorDelete(TestBaseClientDBClass):
    MUTATION = """
        mutation TestMutation($author_id: Int!) {
            delete_author(author_id: $author_id) {
                ... on AuthorNotFound {
                  message
                }
            }
        }
    """

    async def test_delete(self):
        author = await create_test_author()

        response = await self.client.post(
            '/graphql', json={'query': self.MUTATION, 'variables': {'author_id': author.id}}
        )
        assert response.json()['data']['delete_author'] is None

    async def test_delete_not_found(self):
        not_found_id = -9999999

        response = await self.client.post(
            '/graphql', json={'query': self.MUTATION, 'variables': {'author_id': not_found_id}}
        )
        assert response.json()['data']['delete_author'] == {'message': f'Author(id={not_found_id}) Not Found'}
