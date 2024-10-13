import enum

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint, UUID, Enum
from src.database import metadata


class Contrast(enum.Enum):
    # For active points on bonus card count
    greater_than = "greater"
    # For all(active+used) point on bonus card count
    greater_for_all = "greater all"
    # For order items
    count_items_in_order = "count of items"
    define_item_in_order = "define item"


criterion = Table(
    "criterion",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("contrast", Enum(Contrast), nullable=False),
    Column("contrast_value", Double, nullable=False)
)
