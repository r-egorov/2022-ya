import logging

from configargparse import Namespace
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from yashop.utils.pg import create_connect_to_db_task, create_close_db_connection_task
from yashop.api.handlers import create_main_router
from yashop.api.open_api import custom_openapi
from yashop.api.exception_handlers import (
    http_exception_handler,
    validation_error_handler,
)


tags_metadata = [
    {
        "name": "imports",
        "description": "Импортирует новые товары и/или категории.",
    },
]

log = logging.getLogger(__name__)


def create_app(args: Namespace) -> FastAPI:
    app = FastAPI(
        title="yashop",
        description="Test task for Yandex backend-development school",
        openapi_tags=tags_metadata,
    )

    app.include_router(create_main_router())

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    app.add_event_handler("startup", create_connect_to_db_task(app, args))
    app.add_event_handler("shutdown", create_close_db_connection_task(app))

    app.openapi_schema = custom_openapi(app)

    return app
