from fastapi import APIRouter

from yashop.api.handlers import (
    hello,
    imports,
)


def create_main_router() -> APIRouter:
    base_router = APIRouter()

    base_router.include_router(hello.router)
    base_router.include_router(imports.router)

    return base_router