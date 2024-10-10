from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean
from ..database import metadata

ingredient = Table(
    'ingredient',
    metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('product_id', Integer, ForeignKey('product.id'), nullable=False),
    Column('value', Double, nullable=False),
    Column('item_id', Integer, ForeignKey('item.id'), nullable=False),
)

item = Table(
    'item',
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("title", String, unique=True, nullable=False),
    Column("description", String),
    Column("is_active", Boolean, nullable=False, default=True)
)
