"""update action enum with new values

Revision ID: ab665d36a69a
Revises: eac90d4d4fbc
Create Date: 2024-10-13 18:24:21.359768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab665d36a69a'
down_revision: Union[str, None] = 'eac90d4d4fbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Step 1: Add the new ENUM type if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'action') THEN
                CREATE TYPE action AS ENUM (
                    'add_cart_bonuses', 
                    'reduce_card_bonuses', 
                    'reduce_order_sum', 
                    'reduce_order_sum_percent'
                );
            END IF;
        END $$;
    """)

    # Step 2: Alter the 'action' column in the 'benefit' table to use the new ENUM type
    op.execute("""
        ALTER TABLE benefit
        ALTER COLUMN action
        TYPE action USING action::text::action;
    """)


def downgrade():
    # Optional: Rollback the changes if needed
    op.execute("""
        ALTER TABLE benefit
        ALTER COLUMN action
        TYPE VARCHAR;
    """)

    op.execute("DROP TYPE IF EXISTS action;")