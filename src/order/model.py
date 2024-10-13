from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, UUID

from ..auth.models import User
from ..database import metadata

order = Table(
    'order',
    metadata,
    Column('id', BigInteger, primary_key=True),
    Column('user_id', UUID, ForeignKey(User.id)),
    Column('cost', Double, nullable=False),
    Column('date', TIMESTAMP, nullable=False),
    Column('comment', String(255))
)

order_item = Table(
    'order_item',
    metadata,
    Column('id', BigInteger, primary_key=True),
    Column('item_id', BigInteger, ForeignKey('item.id'), nullable=False),
    Column('order_id', BigInteger, ForeignKey('order.id'), nullable=False),
    Column('count', Double, nullable=False),
)

order_item_ingredient = Table(
    "order_item_ingredient",
    metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('product_id', Integer, ForeignKey('product.id'), nullable=False),
    Column('value', Double, nullable=False),
    Column('order_item_id', Integer, ForeignKey('order_item.id'), nullable=False),
)