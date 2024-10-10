from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    PrimaryKeyConstraint

from ..database import metadata

product_value_type = Table(
    'product_value_type',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, unique=True, nullable=False),
)

product = Table(
    'product',
    metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('name', String, unique=True, nullable=False),
    Column('value', Double, nullable=False, default=0),
    Column('value_type_id', Integer, ForeignKey('product_value_type.id'), nullable=False),
    Column('cost_per_one', Double, nullable=False, default=0)
)

shop_product = Table(
    'shop_product',
    metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('shop_id', Integer, ForeignKey('shop.id')),
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('added_at', TIMESTAMP, nullable=False)
)

allergen_product = Table(
    "allergen_product",
    metadata,
    Column("allergen_id", Integer, ForeignKey("allergen.id"), nullable=False),
    Column("product_id", BigInteger, ForeignKey("product.id"), nullable=False),
    PrimaryKeyConstraint("allergen_id", "product_id")
)
