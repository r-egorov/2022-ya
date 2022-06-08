import uuid
from enum import Enum, unique

from sqlalchemy import (
    Column, MetaData, Table,
    String, DateTime, Enum as PgEnum, Integer,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import LtreeType

metadata = MetaData()


@unique
class ShopUnitType(Enum):
    CATEGORY = "CATEGORY"
    OFFER = "OFFER"


units_table = Table(
    "units",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", String, nullable=False),
    Column("unit_code", String, nullable=False),
    Column("date", DateTime, nullable=False),
    Column("parent_id", UUID(as_uuid=True), ForeignKey("units.id"), nullable=True),
    Column("type", PgEnum(ShopUnitType, name="type"), nullable=False),
    Column("price", Integer, nullable=True),
    Column("path", LtreeType, nullable=False),
    Index("ix__units__path", "path", postgresql_using="gist"),
    Index("ix__unique_unit_in_category", "name", "unit_code", "parent_id",
          unique=True,
          postgresql_where="parent_id IS NOT NULL"
          ),
    Index("ix__unique_unit_in_root", "name", "unit_code",
          unique=True,
          postgresql_where="parent_id IS NULL"
          ),
)
