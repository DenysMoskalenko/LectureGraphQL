import json
import os
from typing import Any

from aiofiles import open
import strawberry

from app.core.config import Settings
from app.exceptions import AlreadyExistError, NotFoundError
from app.graphql.authors.service import AuthorService
from app.graphql.books.types import BookType


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
            books = json.loads(await file.read())

        return [_load_book_type(b) for b in books]

    async def get_books_by_author_id(self, author_id: int) -> list[BookType]:
        books = await self.get_books()
        return [b for b in books if b.author_id == author_id]

    async def get_book_by_id(self, book_id: int) -> BookType:
        book = _extract_book(book_id, books=await self.get_books())
        return book

    async def create_book(self, author_id: int, name: str):
        await self._validate_book(author_id, name)

        book = BookType(id=await self._get_next_id(), author_id=author_id, name=name)
        async with open(self.__file_path, 'a') as file:
            await file.write(json.dumps(strawberry.asdict(book)))

    async def _validate_book(self, author_id: int, name: str) -> None:
        await self.__author_service.get_author_by_id(author_id)

        books = await self.get_books()
        for b in books:
            if b.name.lower() == name.lower() and b.author_id == author_id:
                raise AlreadyExistError('Book with this name already exist for this Author')

    async def _get_next_id(self) -> int:
        last_id = max(a.id for a in await self.get_books())
        return last_id + 1

    async def delete_book(self, book_id: int) -> None:
        books = await self.get_books()
        book = _extract_book(book_id, books)

        updated_books = [json.dumps(strawberry.asdict(a)) for a in books if a.id != book.id]
        async with open(self.__file_path, 'w') as f:
            await f.writelines(updated_books)
