import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.extensions import ParserCache, QueryDepthLimiter, ValidationCache
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
from strawberry.tools import merge_types

from app.graphql.authors.queries import AuthorsMutation, AuthorsQuery
from app.graphql.books.queries import BooksMutation, BooksQuery

logging.basicConfig(
    level=logging.INFO,
    format=u'[%(asctime)s] %(levelname)s %(name)s %(message)s',
)


async def _get_context() -> dict:
    from app.core.config import get_settings

    return {
        'settings': get_settings(),
    }


def create_app() -> FastAPI:
    _app = FastAPI(title='LectureAPI', version='0.1.0')

    graphql_router = GraphQLRouter(schema=create_graphql_schema(), context_getter=_get_context)
    _app.include_router(graphql_router, prefix='/graphql')

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    return _app


def create_graphql_schema() -> strawberry.Schema:
    extensions = [
        QueryDepthLimiter(max_depth=3),
        ValidationCache(maxsize=256),
        ParserCache(maxsize=256),
        # MaskErrors(),  # Hide error description. Debug=False
        # ApolloTracingExtension,  # Enable performance tracing
    ]

    queries = (AuthorsQuery, BooksQuery)
    mutations = (AuthorsMutation, BooksMutation)

    return strawberry.Schema(
        query=merge_types('Query', queries),
        mutation=merge_types('Mutation', mutations),
        extensions=extensions,
        config=StrawberryConfig(auto_camel_case=False),
    )


app = create_app()


@app.get('/health-check')
def health_check() -> bool:
    return True
