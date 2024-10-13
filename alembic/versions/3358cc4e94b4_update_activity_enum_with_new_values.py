"""update activity enum with new values

Revision ID: 3358cc4e94b4
Revises: ab665d36a69a
Create Date: 2024-10-13 18:31:30.146734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3358cc4e94b4'
down_revision: Union[str, None] = 'ab665d36a69a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем новый тип ENUM 'activity'
    op.execute("CREATE TYPE activity AS ENUM ('add_cart_bonuses', 'reduce_card_bonuses', 'reduce_order_sum', 'reduce_order_sum_percent')")

    # Явное преобразование с использованием USING
    op.execute("""
        ALTER TABLE benefit 
        ALTER COLUMN action 
        TYPE activity 
        USING action::text::activity
    """)


def downgrade() -> None:
    # Восстанавливаем тип колонки до прежнего с явным преобразованием
    op.execute("""
        ALTER TABLE benefit 
        ALTER COLUMN action 
        TYPE action 
        USING action::text::action
    """)

    # Удаляем тип ENUM 'activity'
    op.execute("DROP TYPE activity")
