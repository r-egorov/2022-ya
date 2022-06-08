import logging
import os
from configargparse import Namespace

from alembic.config import CommandLine

from yashop.utils.pg import (
    make_alembic_config,
    DEFAULT_PG_HOST,
    DEFAULT_PG_PORT,
    DEFAULT_PG_USER,
    DEFAULT_PG_PASSWORD,
    DEFAULT_PG_DB,
)


def parse_arguments(alembic: CommandLine) -> Namespace:
    alembic.parser.add_argument_group('DB Options')
    alembic.parser.add_argument(
        '--pg-user', default=os.getenv('YASHOP_PG_USER', DEFAULT_PG_USER),
        help='Database USER [env var: YASHOP_PG_USER]'
    )
    alembic.parser.add_argument(
        '--pg-password', default=os.getenv('YASHOP_PG_PASSWORD', DEFAULT_PG_PASSWORD),
        help='Database PASSWORD [env var: YASHOP_PG_PASSWORD]'
    )
    alembic.parser.add_argument(
        '--pg-host', default=os.getenv('YASHOP_PG_HOST', DEFAULT_PG_HOST),
        help='Database HOST [env var: YASHOP_PG_HOST]'
    )
    alembic.parser.add_argument(
        '--pg-port', default=os.getenv('YASHOP_PG_PORT', DEFAULT_PG_PORT),
        help='Database PORT [env var: YASHOP_PG_PORT]'
    )
    alembic.parser.add_argument(
        '--pg-db', default=os.getenv('YASHOP_PG_DB', DEFAULT_PG_DB),
        help='Database name in PostgreSQL [env var: YASHOP_PG_DB]'
    )
    return alembic.parser.parse_args()


def main():
    logging.basicConfig(level=logging.DEBUG)

    alembic = CommandLine()
    options = parse_arguments(alembic)
    if 'cmd' not in options:
        alembic.parser.error('too few arguments')
        exit(128)
    else:
        config = make_alembic_config(options)
        exit(alembic.run_cmd(config, options))


if __name__ == "__main__":
    main()
