import json
import os
from typing import Any

from aiofiles import open

from app.core.config import Settings
from app.exceptions import AlreadyExistError, NotFoundError
from app.graphql.authors.service import AuthorService
from app.graphql.books.types import BookType
from app.graphql.converters import strawberry_to_dict


def _load_book_type(book: dict[str, Any]) -> BookType:
    return BookType(id=book['id'], author_id=book['author_id'], name=book['name'])


def _extract_book(book_id: int, books: list[BookType]) -> BookType:
    books = {a.id: a for a in books}
    if book_id not in books:
        raise NotFoundError(f'Book(id={book_id}) Not Found')

    return books[book_id]


class BookService:
    __filename = 'books.json'

    def __init__(self, settings: Settings):
        self.__file_path = os.path.join(settings.DATABASE_PATH, BookService.__filename)
        self.__author_service = AuthorService(settings)

    async def get_books(self) -> list[BookType]:
        async with open(self.__file_path, 'r') as file:
            content = await file.read()
            books = json.loads(content) if content else []

        return [_load_book_type(b) for b in books]

    async def get_books_by_author_id(self, author_id: int) -> list[BookType]:
        books = await self.get_books()
        return [b for b in books if b.author_id == author_id]

    async def get_book_by_id(self, book_id: int) -> BookType:
        book = _extract_book(book_id, books=await self.get_books())
        return book

    async def create_book(self, author_id: int, name: str) -> BookType:
        await self._validate_book(author_id, name)

        books = await self.get_books()

        new_book = BookType(id=await self._get_next_id(), author_id=author_id, name=name)
        books.append(new_book)

        books_data = [strawberry_to_dict(b, exclude={'author'}) for b in books]
        async with open(self.__file_path, 'w') as file:
            await file.write(json.dumps(books_data))

        return new_book

    async def _validate_book(self, author_id: int, name: str) -> None:
        await self.__author_service.get_author_by_id(author_id)

        books = await self.get_books()
        for b in books:
            if b.name.lower() == name.lower() and b.author_id == author_id:
                raise AlreadyExistError('Book with this name already exist for this Author')

    async def _get_next_id(self) -> int:
        books = await self.get_books()
        if not books:
            return 1

        last_id = max(a.id for a in books)
        return last_id + 1

    async def delete_book(self, book_id: int) -> None:
        books = await self.get_books()
        book = _extract_book(book_id, books)

        updated_books = [strawberry_to_dict(b, exclude={'author'}) for b in books if b.id != book.id]
        async with open(self.__file_path, 'w') as f:
            await f.write(json.dumps(updated_books))
