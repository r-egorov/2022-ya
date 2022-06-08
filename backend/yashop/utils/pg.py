import logging
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Union

from alembic.config import Config
from configargparse import Namespace

from sqlalchemy.engine import URL

PROJECT_PATH = Path(__file__).parent.parent.resolve()

DEFAULT_PG_USER = "postgres"
DEFAULT_PG_PASSWORD = "postgres"
DEFAULT_PG_HOST = "localhost"
DEFAULT_PG_PORT = 5432
DEFAULT_PG_DB = "shop"
CENSORED = '***'
MAX_QUERY_ARGS = 32767
MAX_INTEGER = 2147483647

log = logging.getLogger(__name__)


def make_sqlalchemy_url(
        username: str,
        password: str,
        host: str,
        port: str,
        database: str,
        driver: str = "postgresql+asyncpg",
):
    return URL.create(driver, username, password, host, port, database)


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
