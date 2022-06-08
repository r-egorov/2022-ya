from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ValidationError, validator

from yashop.db.schema import ShopUnitType


class ShopUnitImportSchema(BaseModel):
    id: UUID
    name: str
    parentId: Optional[UUID]
    type: ShopUnitType
    price: Optional[int]

    @validator('name')
    def name_not_empty(self, name):
        if len(name) < 1:
            raise ValidationError("name must not be empty")

    @validator('price')
    def price_only_in_offers(self, price, values):
        unit_type = values["type"]
        if (unit_type == ShopUnitType.OFFER and price is None
                or unit_type == ShopUnitType.CATEGORY and price is not None):
            raise ValidationError(
                "categories must not have a price, offers must have a price"
            )


class ImportSchema(BaseModel):
    items: List[ShopUnitImportSchema]
    updateDate: datetime

    @validator('updateDate')
    def date_not_future(self, update_date: datetime):
        if update_date.timestamp() > datetime.now().timestamp():
            raise ValidationError(
                "updateDate cannot be in the future"
            )

    @validator('items')
    def unit_ids_unique(self, units):
        unit_types = set()
        for unit in units:
            if unit.id in unit_types:
                raise ValidationError(
                    f"id {unit.id} is not unique"
                )
            unit_types.add(unit.id)
