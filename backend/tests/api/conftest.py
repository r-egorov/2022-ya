import socket
import asyncio

import pytest
import pytest_asyncio
from alembic.command import upgrade
from sqlalchemy.engine import URL as SaURL
from sqlalchemy import create_engine

from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from yashop.api.__main__ import parser
from yashop.api.app import create_app


@pytest_asyncio.fixture
async def migrated_postgres(alembic_config, postgres):
    upgrade(alembic_config, 'head')
    return postgres


@pytest_asyncio.fixture
def find_free_port():
    def _find_free_port():
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", 0))
        portnum = s.getsockname()[1]
        s.close()

        return portnum

    return _find_free_port


@pytest_asyncio.fixture
def arguments(find_free_port, migrated_postgres: SaURL):
    return parser.parse_args(
        [
            '--log-level=debug',
            '--api-address=127.0.0.1',
            f'--api-port={find_free_port()}',
            f'--pg-user={migrated_postgres.username}',
            f'--pg-password={migrated_postgres.password}',
            f'--pg-host={migrated_postgres.host}',
            f'--pg-port={migrated_postgres.port}',
            f'--pg-db={migrated_postgres.database}',

        ]
    )


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def app(arguments, event_loop):
    app = create_app(arguments)
    async with LifespanManager(app):
        yield app


@pytest_asyncio.fixture
async def api_client(app):
    async with AsyncClient(
            app=app, base_url="http://test", headers={"Content-Type": "application/json"},
    ) as c:
        yield c


@pytest_asyncio.fixture
def migrated_postgres_connection(migrated_postgres):
    engine = create_engine(migrated_postgres)
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
        engine.dispose()
