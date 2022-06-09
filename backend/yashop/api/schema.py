from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, validator, Field

from yashop.db.schema import ShopUnitType


class ShopUnitImportSchema(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID] = Field(alias="parentId")
    type: ShopUnitType
    price: Optional[int]

    class Config:
        allow_population_by_field_name = True

    @validator('name')
    def name_not_empty(cls, name):
        if len(name) < 1:
            raise ValueError('name must not be empty')
        return name

    @validator('price')
    def price_only_in_offers(cls, price, values):
        unit_type = values['type']
        if (unit_type == ShopUnitType.OFFER and price is None
                or unit_type == ShopUnitType.CATEGORY and price is not None):
            raise ValueError(
                'categories must not have a price, offers must have a price'
            )
        if price is not None:
            if price < 1:
                raise ValueError(
                    'price must be positive int, more than one'
                )
        return price



class ImportSchema(BaseModel):
    items: List[ShopUnitImportSchema]
    update_date: datetime = Field(alias="updateDate")

    class Config:
        allow_population_by_field_name = True

    @validator('update_date')
    def date_not_future(cls, update_date: datetime):
        if update_date.timestamp() > datetime.now().timestamp():
            raise ValueError(
                'updateDate cannot be in the future'
            )
        return update_date

    @validator('items')
    def unit_ids_unique(cls, units):
        unit_types = set()
        for unit in units:
            if unit.id in unit_types:
                raise ValueError(
                    f'id {unit.id} is not unique'
                )
            unit_types.add(unit.id)
        return units

    @validator('items')
    def parent_ids_only_categories(cls, units):
        units_types = {}
        parent_ids = set()
        for unit in units:
            units_types[unit.id] = unit.type
            if unit.parent_id is not None:
                parent_ids.add(unit.parent_id)
        for parent_id in parent_ids:
            if parent_id in units_types:
                if units_types[parent_id] == ShopUnitType.OFFER:
                    raise ValueError(
                        'only categories can be parents'
                    )
        return units


class ErrorSchema(BaseModel):
    code: int = 400
    message: str
