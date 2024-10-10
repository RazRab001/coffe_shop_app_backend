from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint, UUID
from ..database import metadata
from src.auth.models import User

comment = Table(
    "comment",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("value", Integer, nullable=False),
    Column("body", String, nullable=False),
    Column("date", TIMESTAMP, nullable=False),
)

comment_user = Table(
    "comment_user",
    metadata,
    Column("comment_id", BigInteger, ForeignKey('comment.id'), nullable=False),
    Column('user_id', UUID, ForeignKey(User.id), nullable=False),
    PrimaryKeyConstraint("comment_id", "user_id")
)

comment_item = Table(
    "comment_item",
    metadata,
    Column("comment_id", BigInteger, ForeignKey('comment.id'), nullable=False),
    Column('item_id', BigInteger, ForeignKey('item.id'), nullable=False),
    PrimaryKeyConstraint("comment_id", "item_id")
)
