from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint, UUID
from ..database import metadata
from src.auth.models import User

bonus_card = Table(
    "bonus_card",
    metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('user_id', UUID, ForeignKey(User.id)),
    Column('phone', String(20), nullable=False),
    Column('count', Integer, default=0),
    Column('used_points', Integer, default=0)
)
