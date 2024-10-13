"""update benefits enum

Revision ID: eac90d4d4fbc
Revises: cba5851e9c16
Create Date: 2024-10-13 18:16:50.538069

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'eac90d4d4fbc'
down_revision: Union[str, None] = 'cba5851e9c16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create ENUM type 'action' only if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'action') THEN
                CREATE TYPE action AS ENUM ('add_cart_bonuses', 'reduce_card_bonuses', 'reduce_order_sum', 'reduce_order_sum_percent');
            END IF;
        END $$;
    """)

    # Step 2: Alter the 'action' column in the 'benefit' table to use the new ENUM type with a cast
    op.execute("""
        ALTER TABLE benefit
        ALTER COLUMN action
        TYPE action USING action::text::action;
    """)

    # (Optional) Step 3: Drop the old ENUM type if it's no longer needed
    op.execute("""
        DROP TYPE IF EXISTS action_old;
    """)


def downgrade() -> None:
    # Rollback Step 1: Create the old ENUM type if necessary
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'action_old') THEN
                CREATE TYPE action_old AS ENUM ('add_cart_bonuses', 'reduce_card_bonuses', 'reduce_order_sum', 'reduce_order_sum_percent');
            END IF;
        END $$;
    """)

    # Rollback Step 2: Revert the 'action' column to use the old ENUM type
    op.execute("""
        ALTER TABLE benefit
        ALTER COLUMN action
        TYPE action_old USING action::text::action_old;
    """)

    # Rollback Step 3: Drop the new ENUM type if it exists
    op.execute("""
        DROP TYPE IF EXISTS action;
    """)
