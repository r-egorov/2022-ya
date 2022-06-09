import uuid
from datetime import datetime, timedelta
from typing import Optional

import pytest
from pydantic import ValidationError

from yashop.api.schema import ShopUnitImportSchema, ImportSchema


def generate_unit_dict(
        id_: uuid.UUID = uuid.uuid4(),
        name: str = 'Default name',
        parent_id: Optional[uuid.UUID] = None,
        type_: str = 'OFFER',
        price: Optional[int] = 100,
):
    return {
        'id': str(id_),
        'name': name,
        'parentId': str(parent_id) if parent_id is not None else None,
        'type': type_,
        'price': price,
    }


class TestImportSchemas:
    @staticmethod
    def assert_eq_unit_dict_and_schema(unit_dict, unit_schema: ShopUnitImportSchema):
        unit_schema_parent_id = str(unit_schema.parent_id) if unit_schema is not None else None
        assert unit_dict['id'] == str(unit_schema.id)
        assert unit_dict['name'] == unit_schema.name
        assert unit_dict['parentId'] == unit_schema_parent_id
        assert unit_dict['type'] == str(unit_schema.type.value)
        assert unit_dict['price'] == unit_schema.price

    def test_shop_unit_import_schema_no_price_in_offer(self):
        unit = generate_unit_dict(price=None)
        with pytest.raises(ValidationError,
                           match='categories must not have a price, offers must have a price'):
            ShopUnitImportSchema(**unit)

    def test_shop_unit_import_schema_price_in_category(self):
        unit = generate_unit_dict(type_='CATEGORY')
        with pytest.raises(ValidationError,
                           match='categories must not have a price, offers must have a price'):
            ShopUnitImportSchema(**unit)

    def test_shop_unit_import_schema_empty_name(self):
        unit = generate_unit_dict(name='')
        with pytest.raises(ValidationError, match='name must not be empty'):
            ShopUnitImportSchema(**unit)

    def test_shop_unit_import_schema_ok(self):
        offer = generate_unit_dict(name='offer', parent_id=uuid.uuid4())
        category = generate_unit_dict(name='category', type_='CATEGORY',
                                      price=None, parent_id=uuid.uuid4())
        offer_schema = ShopUnitImportSchema(**offer)
        category_schema = ShopUnitImportSchema(**category)

        self.assert_eq_unit_dict_and_schema(offer, offer_schema)
        self.assert_eq_unit_dict_and_schema(category, category_schema)

    def test_import_schema_ok(self):
        upd_date = datetime.now() - timedelta(days=10)
        category = generate_unit_dict(id_=uuid.uuid4(), type_='CATEGORY',
                                      price=None)
        offer = generate_unit_dict(id_=uuid.uuid4(), type_='OFFER')

        import_schema = ImportSchema(
            updateDate=upd_date,
            items=[category, offer],
        )

    def test_import_schema_date_in_future(self):
        future = datetime.now() + timedelta(days=10)
        category = generate_unit_dict(id_=uuid.uuid4(), type_='CATEGORY',
                                      price=None)
        offer = generate_unit_dict(id_=uuid.uuid4(), type_='OFFER')
        with pytest.raises(ValidationError, match='updateDate cannot be in the future'):
            ImportSchema(
                updateDate=future,
                items=[category, offer],
            )

    def test_import_schema_not_unique_ids(self):
        upd_date = datetime.now() - timedelta(days=10)
        id_ = uuid.uuid4()
        category = generate_unit_dict(id_=id_, type_='CATEGORY',
                                      price=None)
        offer = generate_unit_dict(id_=id_, type_='OFFER')

        with pytest.raises(ValidationError, match=f'id {id_} is not unique'):
            ImportSchema(
                updateDate=upd_date,
                items=[category, offer],
            )
    
    def test_import_schema_offer_as_parent(self):
        upd_date = datetime.now() - timedelta(days=10)
        category = generate_unit_dict(id_=uuid.uuid4(), type_='CATEGORY',
                                      price=None)
        offer_id = uuid.uuid4()
        offer = generate_unit_dict(id_=offer_id, type_='OFFER')
        child_offer = generate_unit_dict(id_=uuid.uuid4(), type_='OFFER', parent_id=offer_id)

        with pytest.raises(ValidationError, match='only categories can be parents'):
            ImportSchema(
                updateDate=upd_date,
                items=[category, offer, child_offer],
            )
        
