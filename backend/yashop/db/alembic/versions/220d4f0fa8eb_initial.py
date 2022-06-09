"""Initial

Revision ID: 220d4f0fa8eb
Revises: 
Create Date: 2022-06-06 15:44:57.907521

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Enum
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '220d4f0fa8eb'
down_revision = None
branch_labels = None
depends_on = None

ShopUnitType = Enum("CATEGORY", "OFFER", name="type")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree;")

    op.create_table(
        'units',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('unit_code', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('type', ShopUnitType, nullable=False),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('path', sqlalchemy_utils.types.ltree.LtreeType(), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix__unique_unit_in_category', 'units', ['name', 'unit_code', 'parent_id'], unique=True, postgresql_where='parent_id IS NOT NULL')
    op.create_index('ix__unique_unit_in_root', 'units', ['name', 'unit_code'], unique=True, postgresql_where='parent_id IS NULL')
    op.create_index('ix__units__path', 'units', ['path'], unique=False, postgresql_using='gist')

    op.execute("""
        CREATE OR REPLACE FUNCTION update_units_path() RETURNS TRIGGER AS $$
        DECLARE
            tree_path ltree;
        BEGIN
            NEW.unit_code = REPLACE(NEW.name, ' ', '_');
            IF NEW.parent_id IS NULL THEN
                NEW.path = NEW.unit_code::ltree;
            ELSEIF TG_OP = 'INSERT' OR OLD.parent_id IS NULL OR OLD.parent_id != NEW.parent_id THEN
                SELECT "path" FROM units WHERE id = NEW.parent_id INTO tree_path;
                IF tree_path IS NULL THEN
                    RAISE EXCEPTION 'Invalid parent_id %', NEW.parent_id;
                END IF;
                NEW.path = tree_path || NEW.unit_code;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER path_tgr
        BEFORE INSERT OR UPDATE ON units
        FOR EACH ROW EXECUTE PROCEDURE update_units_path();
    """)


def downgrade() -> None:
    op.execute("""
           DROP TRIGGER "path_tgr" ON units;
           DROP FUNCTION update_units_path();
       """)
    op.drop_table('units')
    ShopUnitType.drop(op.get_bind())
    op.execute("DROP EXTENSION ltree;")

