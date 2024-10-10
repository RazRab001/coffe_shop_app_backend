from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double

from ..database import metadata

shop = Table(
    'shop',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, unique=True, nullable=False)
)
