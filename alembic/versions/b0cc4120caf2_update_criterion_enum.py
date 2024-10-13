"""update criterion enum

Revision ID: b0cc4120caf2
Revises: 7c229bfe62ff
Create Date: 2024-10-13 17:46:34.364004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b0cc4120caf2'
down_revision: Union[str, None] = '7c229bfe62ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Step 1: Create the new ENUM type if it does not exist ###
    op.execute("""
        CREATE TYPE contrast AS ENUM ('greater_than', 'greater_for_all', 'count_items_in_order', 'define_item_in_order');
    """)

    # ### Step 2: Alter the column to use the new ENUM type with a cast ###
    op.execute("""
        ALTER TABLE criterion 
        ALTER COLUMN contrast 
        TYPE contrast USING contrast::text::contrast;
    """)

    # The following DROP is optional and can be skipped if you don't want to remove the old ENUM
    # ### Step 3: Drop the old ENUM type if it's not needed anymore ###
    op.execute("""
        DROP TYPE IF EXISTS contrast_old;
    """)


def downgrade() -> None:
    # ### Rollback Step 1: Create the old ENUM type if necessary ###
    op.execute("""
        CREATE TYPE contrast_old AS ENUM ('greater_than', 'greater_for_all', 'count_items_in_order', 'define_item_in_order');
    """)

    # ### Rollback Step 2: Revert the column back to the old ENUM type ###
    op.execute("""
        ALTER TABLE criterion 
        ALTER COLUMN contrast 
        TYPE contrast_old USING contrast::text::contrast_old;
    """)

    # ### Rollback Step 3: Drop the new ENUM type ###
    op.execute("""
        DROP TYPE contrast;
    """)

