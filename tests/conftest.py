import asyncio
import os
import pathlib

from fastapi import FastAPI
from httpx import AsyncClient
import pytest

TEST_HOST = 'http://test'
TEST_DB = os.path.join(pathlib.Path(os.path.dirname(os.path.realpath(__file__))), 'db')


def pytest_configure(config: pytest.Config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    os.environ['DATABASE_PATH'] = TEST_DB


@pytest.fixture(scope='session')
async def app() -> FastAPI:
    from app.main import create_app

    _app = create_app()

    yield _app


@pytest.fixture(scope='session')
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url=TEST_HOST) as client:
        yield client


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


class TestBaseDBClass:
    """Provides Test Class with loaded database fixture"""

    @pytest.fixture(autouse=True, scope='function')
    def _provide_db(self):
        """Provides empty database for all tests in class"""
        all_db_files = os.listdir(TEST_DB)
        for file_path in all_db_files:
            open(os.path.join(TEST_DB, file_path), 'w').close()


class TestBaseClientClass:
    """Provides Test Class with loaded client fixture"""

    @pytest.fixture(autouse=True)
    def _provide_client(self, client: AsyncClient):
        """Provides client for all tests in class"""
        self.client = client


class TestBaseClientDBClass(TestBaseClientClass, TestBaseDBClass):
    """Provides Test Class with loaded database and client fixture"""
