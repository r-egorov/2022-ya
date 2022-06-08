import logging

from fastapi import FastAPI
from configargparse import Namespace

from yashop.utils.pg import create_connect_to_db_task, create_close_db_connection_task
from yashop.api.handlers import create_main_router

log = logging.getLogger(__name__)


def create_app(args: Namespace) -> FastAPI:
    app = FastAPI(
        title="yashop",
        description="Test task for Yandex backend-development school",
    )

    app.include_router(create_main_router())

    app.add_event_handler("startup", create_connect_to_db_task(app, args))
    app.add_event_handler("shutdown", create_close_db_connection_task(app))

    return app
