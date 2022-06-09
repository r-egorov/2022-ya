import os
import uuid
from types import SimpleNamespace

import pytest
from sqlalchemy_utils import create_database, drop_database

from yashop.utils.pg import (
    make_sqlalchemy_url,
    make_alembic_config,
    DEFAULT_PG_HOST,
    DEFAULT_PG_PORT,
    DEFAULT_PG_USER,
    DEFAULT_PG_PASSWORD,
    DEFAULT_PG_DB,
)

PG_HOST = os.getenv('YASHOP_PG_HOST', DEFAULT_PG_HOST)
PG_PORT = os.getenv('YASHOP_PG_PORT', DEFAULT_PG_PORT)
PG_USER = os.getenv('YASHOP_PG_USER', DEFAULT_PG_USER)
PG_PASSWORD = os.getenv('YASHOP_PG_PASSWORD', DEFAULT_PG_PASSWORD)
PG_DB = os.getenv('YASHOP_PG_DB', DEFAULT_PG_DB)


@pytest.fixture
def postgres():
    tmp_name = '.'.join([uuid.uuid4().hex, 'pytest'])
    tmp_url = make_sqlalchemy_url(
        username=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT,
        database=tmp_name,
        driver="postgresql",
    )
    create_database(str(tmp_url))
    try:
        yield tmp_url
    finally:
        drop_database(str(tmp_url))



@pytest.fixture()
def alembic_config(postgres):
    cmd_options = SimpleNamespace(config='alembic.ini',
                                  name='alembic',
                                  pg_user=postgres.username,
                                  pg_password=postgres.password,
                                  pg_host=postgres.host,
                                  pg_port=postgres.port,
                                  pg_db=postgres.database,
                                  raiseerr=False,
                                  x=None)
    return make_alembic_config(cmd_options)