import enum

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint, UUID, Enum
from src.database import metadata


class Action(enum.Enum):
    add = "+"
    reduce = "-"


benefit = Table(
    "benefit",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("action", Enum(Action), nullable=False),
    Column("action_value", Double, nullable=False)
)
