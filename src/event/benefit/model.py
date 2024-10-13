import enum

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint, UUID, Enum
from src.database import metadata


class Activity(enum.Enum):
    add_cart_bonuses = "add_cart_bonuses"
    reduce_card_bonuses = "reduce_card_bonuses"
    reduce_order_sum = "reduce_order_sum"
    reduce_order_sum_percent = "reduce_order_sum_percent"


benefit = Table(
    "benefit",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("action", Enum(Activity), nullable=False),
    Column("action_value", Double, nullable=False)
)
