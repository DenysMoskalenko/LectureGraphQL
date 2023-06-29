from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    author_id: int
    name: str = Field(..., min_length=2, max_length=64)

    class Config:
        schema_extra = {
            'example': {
                'author_id': 1,
                'name': '1984',
            }
        }
