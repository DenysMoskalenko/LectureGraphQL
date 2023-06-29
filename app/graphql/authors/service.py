import json
import os
from typing import Any

from aiofiles import open

from app.core.config import Settings
from app.exceptions import AlreadyExistError, NotFoundError
from app.graphql.authors.types import AuthorType
from app.graphql.converters import strawberry_to_dict


def _load_author_type(author: dict[str, Any]) -> AuthorType:
    return AuthorType(id=author['id'], name=author['name'])


def _extract_author(author_id: int, authors: list[AuthorType]) -> AuthorType:
    authors = {a.id: a for a in authors}
    if author_id not in authors:
        raise NotFoundError(f'Author(id={author_id}) Not Found')

    return authors[author_id]


class AuthorService:
    __filename = 'authors.json'

    def __init__(self, settings: Settings):
        self.__file_path = os.path.join(settings.DATABASE_PATH, AuthorService.__filename)

    async def get_authors(self) -> list[AuthorType]:
        async with open(self.__file_path, 'r') as file:
            content = await file.read()
            authors = json.loads(content) if content else []

        authors = [_load_author_type(a) for a in authors]
        return authors

    async def get_author_by_id(self, author_id: int) -> AuthorType:
        author = _extract_author(author_id, authors=await self.get_authors())
        return author

    async def create_author(self, name: str) -> AuthorType:
        await self._validate_author(name)
        authors = await self.get_authors()

        new_author = AuthorType(id=await self._get_next_id(), name=name)
        authors.append(new_author)

        authors_data = [strawberry_to_dict(a, exclude={'books'}) for a in authors]
        async with open(self.__file_path, 'w') as file:
            await file.write(json.dumps(authors_data))

        return new_author

    async def _validate_author(self, name: str) -> None:
        authors = await self.get_authors()
        for a in authors:
            if a.name.lower() == name.lower():
                raise AlreadyExistError('Author with this name already exist')

    async def _get_next_id(self) -> int:
        authors = await self.get_authors()
        if not authors:
            return 1

        last_id = max(a.id for a in authors)
        return last_id + 1

    async def delete_author(self, author_id: int) -> None:
        authors = await self.get_authors()
        author = _extract_author(author_id, authors)

        updated_authors = [strawberry_to_dict(a, exclude={'books'}) for a in authors if a.id != author.id]
        async with open(self.__file_path, 'w') as f:
            await f.write(json.dumps(updated_authors))
