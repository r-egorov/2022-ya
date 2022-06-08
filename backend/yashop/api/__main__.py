import argparse
import os
from sys import argv

from configargparse import ArgumentParser
from setproctitle import setproctitle
import uvicorn

from yashop.api.app import create_app
from yashop.utils.argparse import clear_environ, positive_int
from yashop.utils.pg import (
    DEFAULT_PG_HOST,
    DEFAULT_PG_PORT,
    DEFAULT_PG_USER,
    DEFAULT_PG_PASSWORD,
    DEFAULT_PG_DB,
)

ENV_VAR_PREFIX = 'YASHOP_'


parser = ArgumentParser(
    auto_env_var_prefix=ENV_VAR_PREFIX, allow_abbrev=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

group = parser.add_argument_group('API Options')
group.add_argument('--api-address', default='0.0.0.0',
                   help='IPv4/IPv6 address API server would listen on')
group.add_argument('--api-port', type=positive_int, default=8081,
                   help='TCP port API server would listen on')

group = parser.add_argument_group('PostgreSQL options')
group.add_argument(
    '--pg-user', default=os.getenv('YASHOP_PG_USER', DEFAULT_PG_USER),
    help='PostgreSQL USER [env var: YASHOP_PG_USER]'
)
group.add_argument(
    '--pg-password', default=os.getenv('YASHOP_PG_PASSWORD', DEFAULT_PG_PASSWORD),
    help='PostgreSQL PASSWORD [env var: YASHOP_PG_PASSWORD]'
)
group.add_argument(
    '--pg-host', default=os.getenv('YASHOP_PG_HOST', DEFAULT_PG_HOST),
    help='PostgreSQL HOST [env var: YASHOP_PG_HOST]'
)
group.add_argument(
    '--pg-port', default=os.getenv('YASHOP_PG_PORT', DEFAULT_PG_PORT),
    help='PostgreSQL PORT [env var: YASHOP_PG_PORT]'
)
group.add_argument(
    '--pg-db', default=os.getenv('YASHOP_PG_DB', DEFAULT_PG_DB),
    help='Database name in PostgreSQL [env var: YASHOP_PG_DB]'
)

group = parser.add_argument_group('Logging options')
group.add_argument('--log-level', default='info',
                   choices=('debug', 'info', 'warning', 'error', 'fatal'))


def main():
    args = parser.parse_args()

    clear_environ(lambda i: i.startswith(ENV_VAR_PREFIX))
    setproctitle(os.path.basename(argv[0]))

    app = create_app(args)
    uvicorn.run(
        app,
        host=args.api_address,
        port=args.api_port,
        log_level=args.log_level,
    )


if __name__ == '__main__':
    main()