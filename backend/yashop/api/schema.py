from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, validator

from yashop.db.schema import ShopUnitType


class ShopUnitImportSchema(BaseModel):
    id: UUID
    name: str
    parentId: Optional[UUID]
    type: ShopUnitType
    price: Optional[int]

    @validator('name')
    def name_not_empty(cls, name):
        if len(name) < 1:
            raise ValueError("name must not be empty")

    @validator('price')
    def price_only_in_offers(cls, price, values):
        unit_type = values["type"]
        if (unit_type == ShopUnitType.OFFER and price is None
                or unit_type == ShopUnitType.CATEGORY and price is not None):
            raise ValueError(
                "categories must not have a price, offers must have a price"
            )
        if price is not None:
            if price < 1:
                raise ValueError(
                    "price must be positive int, more than one"
                )



class ImportSchema(BaseModel):
    items: List[ShopUnitImportSchema]
    updateDate: datetime

    @validator('updateDate')
    def date_not_future(cls, update_date: datetime):
        if update_date.timestamp() > datetime.now().timestamp():
            raise ValueError(
                "updateDate cannot be in the future"
            )

    @validator('items')
    def unit_ids_unique(cls, units):
        unit_types = set()
        for unit in units:
            if unit.id in unit_types:
                raise ValueError(
                    f"id {unit.id} is not unique"
                )
            unit_types.add(unit.id)


class ErrorSchema(BaseModel):
    code: int
    message: str
