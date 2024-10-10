import enum

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint, UUID, Enum
from src.database import metadata


class Contrast(enum.Enum):
    greater_than = ">"
    less_than = "<"
    equal_to = "="
    divisible_by = "%"


criterion = Table(
    "criterion",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("contrast", Enum(Contrast), nullable=False),
    Column("contrast_value", Double, nullable=False)
)
