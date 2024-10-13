"""update criterion enum DB

Revision ID: 7c229bfe62ff
Revises: 308642ff7c45
Create Date: 2024-10-13 17:42:11.320910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c229bfe62ff'
down_revision: Union[str, None] = '308642ff7c45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Определяем новый тип enum для использования в обновлении
new_contrast_enum = sa.Enum(
    'greater_than',
    'greater_for_all',
    'count_items_in_order',
    'define_item_in_order',
    name='contrast_new'
)

old_contrast_enum = sa.Enum(
    'greater_than',
    'greater',
    'less_than',
    name='contrast'
)


def upgrade() -> None:
    # 1. Создаем новый тип enum с нужными значениями
    new_contrast_enum.create(op.get_bind())

    # 2. Обновляем столбец contrast, чтобы использовать новый тип
    op.alter_column(
        'criterion', 'contrast',
        type_=new_contrast_enum,
        postgresql_using="contrast::text::contrast_new"
    )

    # 3. Удаляем старый тип enum
    old_contrast_enum.drop(op.get_bind(), checkfirst=False)


def downgrade() -> None:
    # 1. Создаем старый тип enum
    old_contrast_enum.create(op.get_bind())

    # 2. Обновляем столбец, чтобы вернуть старый тип
    op.alter_column(
        'criterion', 'contrast',
        type_=old_contrast_enum,
        postgresql_using="contrast::text::contrast"
    )

    # 3. Удаляем новый тип enum
    new_contrast_enum.drop(op.get_bind(), checkfirst=False)
