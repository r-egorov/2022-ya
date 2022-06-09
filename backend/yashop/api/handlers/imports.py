from fastapi import APIRouter

from yashop.api.schema import ShopUnitImportSchema, ImportSchema


router = APIRouter()


from fastapi.exceptions import HTTPException

@router.post(
    "/imports", tags=["imports"],
)
async def imports(import_: ImportSchema):
    print(ImportSchema.schema())
    raise HTTPException(status_code=400, detail="loh")
    return({"hello": "world"})