from app.graphql.books.service import BookService
from app.graphql.books.types import BookType
from app.graphql.converters import strawberry_to_dict
from tests.conftest import TestBaseClientDBClass
from tests.factories import BookFactory
from tests.graphql.test_authors import create_test_author


async def create_test_book(*, author_id: int | None = None, name: str | None = None) -> BookType:
    from app.core.config import get_settings

    author_id = author_id or (await create_test_author()).id

    book_factory = BookFactory(author_id=author_id, name=name) if name is not None else BookFactory(author_id=author_id)

    service = BookService(settings=get_settings())
    return await service.create_book(author_id=author_id, name=book_factory.name)


class TestbookList(TestBaseClientDBClass):
    QUERY = """
        query TestQuery {
            books {
                id
            }
        }
    """

    async def test_get_empty(self):
        response = await self.client.post('/graphql', json={'query': self.QUERY})

        response_data = response.json()['data']['books']
        assert response_data == []

    async def test_list(self):
        book1, book2 = await create_test_book(), await create_test_book()

        response = await self.client.post('/graphql', json={'query': self.QUERY})

        response_data = response.json()['data']['books']
        assert response_data == [
            {'id': book1.id},
            {'id': book2.id},
        ]


class TestbookGet(TestBaseClientDBClass):
    QUERY = """
        query TestQuery($book_id: Int!) {
            book(book_id: $book_id) {
                ... on Book {
                    id
                    author_id
                    name
                    author {
                        id
                        name
                    }
                }
                ... on BookNotFound {
                    message
                }
            }
        }
    """

    async def test_get(self):
        author = await create_test_author()
        book = await create_test_book(author_id=author.id)

        response = await self.client.post(
            '/graphql', json={'query': self.QUERY, 'variables': {'book_id': book.id}}
        )

        response_data = response.json()['data']['book']
        assert response_data == {
            **strawberry_to_dict(book, exclude={'author'}),
            'author': strawberry_to_dict(author, exclude={'books'}),
        }

    async def test_not_found(self):
        unreal_id = -99999999

        response = await self.client.post(
            '/graphql', json={'query': self.QUERY, 'variables': {'book_id': unreal_id}}
        )

        response_data = response.json()['data']['book']
        assert response_data == {'message': f'Book(id={unreal_id}) Not Found'}


class TestbookCreate(TestBaseClientDBClass):
    MUTATION = """
        mutation TestMutation($author_id: Int!, $name: String!) {
            create_book(input_schema: {author_id: $author_id, name: $name}) {
                ... on Book {
                    id
                    author_id
                    name
                }
                ... on ValidationError {
                    message
                }
                ... on BookAlreadyExist {
                    message
                }
            }
        }
    """

    async def test_create(self):
        author = await create_test_author()
        book_factory = BookFactory(author_id=author.id)

        response = await self.client.post(
            '/graphql', json={'query': self.MUTATION, 'variables': book_factory.variables()}
        )

        response_data = response.json()['data']['create_book']
        assert response_data['name'] == book_factory.name
        assert response_data['author_id'] == author.id

    async def test_create_not_unique(self):
        exist_book = await create_test_book()
        book_factory = BookFactory(author_id=exist_book.author_id)

        response = await self.client.post(
            '/graphql',
            json={
                'query': self.MUTATION,
                'variables': {**book_factory.variables(), 'name': exist_book.name},
            },
        )

        assert response.json()['data']['create_book'] == {
            'message': 'Book with this name already exist for this Author'
        }


class TestbookDelete(TestBaseClientDBClass):
    MUTATION = """
        mutation TestMutation($book_id: Int!) {
            delete_book(book_id: $book_id) {
                ... on BookNotFound {
                  message
                }
            }
        }
    """

    async def test_delete(self):
        book = await create_test_book()

        response = await self.client.post(
            '/graphql', json={'query': self.MUTATION, 'variables': {'book_id': book.id}}
        )
        assert response.json()['data']['delete_book'] is None

    async def test_delete_not_found(self):
        not_found_id = -9999999

        response = await self.client.post(
            '/graphql', json={'query': self.MUTATION, 'variables': {'book_id': not_found_id}}
        )
        assert response.json()['data']['delete_book'] == {'message': f'Book(id={not_found_id}) Not Found'}
