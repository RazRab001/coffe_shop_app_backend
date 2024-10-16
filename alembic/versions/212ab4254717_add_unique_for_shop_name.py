"""add unique for shop name

Revision ID: 212ab4254717
Revises: 05bf180017f8
Create Date: 2024-10-03 19:46:21.834061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '212ab4254717'
down_revision: Union[str, None] = '05bf180017f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'shops', ['name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shops', type_='unique')
    # ### end Alembic commands ###
