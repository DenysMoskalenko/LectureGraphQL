from pydantic import BaseModel, Field, validator


class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=64)

    @validator('name')
    def valid_name(cls, name: str) -> str:
        if name.lower() == 'adolf hitler':
            raise ValueError("We don't do that here...")

        return name

    class Config:
        schema_extra = {
            'example': {
                'name': 'George Orwell',
            }
        }
