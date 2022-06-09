from fastapi import APIRouter

from yashop.api.handlers import (
    imports,
)


def create_main_router() -> APIRouter:
    base_router = APIRouter()

    base_router.include_router(imports.router)

    return base_router