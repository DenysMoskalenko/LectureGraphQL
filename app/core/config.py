from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_PATH: str = 'app/db'

    class Config:
        case_sensitive = True
        frozen = True
        env_file = '.env'


@lru_cache
def get_settings() -> Settings:
    return Settings()
