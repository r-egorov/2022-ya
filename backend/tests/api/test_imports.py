import pytest
import json
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from yashop.api.schema import ImportSchema, RequestImportsSchema
from yashop.db.schema import units_table
from tests.utils.generate import generate_import_unit_dict


pytestmark = pytest.mark.asyncio


class TestImportsHandler:
    URL = '/imports'

    async def test_imports_ok(self, api_client, migrated_postgres_connection):
        upd_date = datetime.now(tz=timezone.utc) - timedelta(days=10)

        offer1 = generate_import_unit_dict(id_=uuid.uuid4(), name='offer1')
        category1 = generate_import_unit_dict(id_=uuid.uuid4(), name='category1', type_='CATEGORY', price=None)
        category2 = generate_import_unit_dict(id_=uuid.uuid4(), name='category2', type_='CATEGORY', price=None)
        offer2 = generate_import_unit_dict(id_=uuid.uuid4(), name='offer2', parent_id=category1['id'])
        offer3 = generate_import_unit_dict(id_=uuid.uuid4(), name='offer3', parent_id=category2['id'])

        req = RequestImportsSchema(**{
            'data': {
                'items': [offer1, category1, category2, offer2, offer3],
                'updateDate': upd_date,
            },
        })

        res = await api_client.post(
            self.URL,
            data=req.json(),
        )
        assert res.status_code == 200

        with migrated_postgres_connection as conn:
            query = units_table.select()
            r = conn.execute(query)

        print(r)