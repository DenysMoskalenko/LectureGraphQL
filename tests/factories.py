from dataclasses import asdict, dataclass, field
import json

from faker import Faker

faker = Faker()


@dataclass(slots=True, kw_only=True)
class BaseFactory:
    def variables(self) -> dict:
        return asdict(self)

    def json(self) -> str:
        return json.dumps(self.variables())


@dataclass(slots=True, kw_only=True)
class AuthorFactory(BaseFactory):
    name: str = field(default_factory=faker.name)


@dataclass(slots=True, kw_only=True)
class BookFactory(BaseFactory):
    author_id: int
    name: str = field(default_factory=lambda: faker.text(max_nb_chars=64).title())
