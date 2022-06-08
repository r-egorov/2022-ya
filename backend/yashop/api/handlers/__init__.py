from fastapi import APIRouter

from yashop.api.handlers import (
    hello,
)


def create_main_router() -> APIRouter:
    base_router = APIRouter()

    base_router.include_router(hello.router)

    return base_router