from typing import List, Dict

from fastapi import (
    APIRouter, Request, Response, status,
)
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncEngine

from yashop.api.schema import ShopUnitImportSchema, ImportSchema
from yashop.db.schema import units_table

router = APIRouter()


def prepare_import_rows(import_: ImportSchema) -> List[Dict]:
    return [
        {
            "id": item.id,
            "name": item.name,
            "date": import_.update_date,
            "parent_id": item.parent_id,
            "type": item.type,
            "price": item.price,
        } for item in import_.items
    ]


@router.post(
    "/imports", tags=["imports"], status_code=status.HTTP_200_OK
)
async def imports(import_: ImportSchema, request: Request):
    db: AsyncEngine = request.app.state.db

    async with db.begin() as conn:
        rows = prepare_import_rows(import_)
        query = units_table.insert().values(rows)
        await conn.execute(query)

    return Response(status_code=status.HTTP_200_OK)