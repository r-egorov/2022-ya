from fastapi import (
    APIRouter, Request, Response, status,
)
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncEngine

from yashop.api.schema import ShopUnitImportSchema, ImportSchema
from yashop.db.schema import units_table

router = APIRouter()


@router.post(
    "/imports", tags=["imports"], status_code=status.HTTP_200_OK
)
async def imports(import_: ImportSchema, request: Request):
    db: AsyncEngine = request.app.state.db

    async with db.begin() as conn:
        query = units_table.insert().values([item.dict() for item in import_.items])
        await conn.execute(query)


    return Response(status_code=status.HTTP_200_OK)