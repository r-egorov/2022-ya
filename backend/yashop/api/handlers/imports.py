from fastapi import (
    APIRouter, Request, Response, status,
)

from yashop.api.schema import ShopUnitImportSchema, ImportSchema


router = APIRouter()


@router.post(
    "/imports", tags=["imports"], status_code=status.HTTP_200_OK
)
async def imports(import_: ImportSchema, request: Request):

    return Response(status_code=status.HTTP_200_OK)