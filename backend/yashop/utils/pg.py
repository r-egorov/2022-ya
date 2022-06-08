import logging
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Union, Callable

from fastapi import FastAPI
from configargparse import Namespace
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import URL as SaURL
from sqlalchemy.ext.asyncio import create_async_engine

PROJECT_PATH = Path(__file__).parent.parent.resolve()

DEFAULT_PG_USER = "postgres"
DEFAULT_PG_PASSWORD = "postgres"
DEFAULT_PG_HOST = "localhost"
DEFAULT_PG_PORT = 5432
DEFAULT_PG_DB = "shop"
CENSORED = '***'
MAX_QUERY_ARGS = 32767
MAX_INTEGER = 2147483647


log = logging.getLogger('uvicorn')


def make_sqlalchemy_url(
        username: str,
        password: str,
        host: str,
        port: str,
        database: str,
        driver: str = "postgresql+asyncpg",
):
    return SaURL.create(driver, username, password, host, port, database)


def make_alembic_config(cmd_opts: Union[Namespace, SimpleNamespace],
                        base_path: str = PROJECT_PATH) -> Config:
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name,
                    cmd_opts=cmd_opts)

    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option('script_location',
                               os.path.join(base_path, alembic_location))

    if cmd_opts.pg_host:
        db_url = make_sqlalchemy_url(
            cmd_opts.pg_user,
            cmd_opts.pg_password,
            cmd_opts.pg_host,
            cmd_opts.pg_port,
            cmd_opts.pg_db,
            driver="postgresql",
        )
        config.set_main_option('sqlalchemy.url', str(db_url))

    return config


def create_connect_to_db_task(app: FastAPI, args: Namespace) -> Callable:
    db_url = make_sqlalchemy_url(
        args.pg_user,
        args.pg_password,
        args.pg_host,
        args.pg_port,
        args.pg_db,
    )

    async def connect_to_db_task() -> None:
        log.info('Connecting to database')
        engine = create_async_engine(
            db_url,
            echo=True,
            future=True,
        )
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1;'))
        log.info('Connected to database')
        app.state.db = engine

    return connect_to_db_task


def create_close_db_connection_task(app: FastAPI) -> Callable:
    async def close_db_connection_task() -> None:
        log.info('Disconnecting from database')
        await app.state.db.dispose()
        log.info('Disconnected from database')

    return close_db_connection_task