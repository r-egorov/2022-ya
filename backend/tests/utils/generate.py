import uuid
from typing import Optional


def generate_import_unit_dict(
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
