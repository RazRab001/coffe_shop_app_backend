from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint
from ..database import metadata

allergen = Table(
    "allergen",
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, unique=True, nullable=False)
)