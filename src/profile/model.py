import enum

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint, UUID, Float
from ..database import metadata
from src.auth.models import User

user_allergen = Table(
    'user_allergen',
    metadata,
    Column('user_id', UUID, ForeignKey(User.id), primary_key=True),
    Column('allergen_id', Integer, ForeignKey('allergen.id'), primary_key=True),
    PrimaryKeyConstraint('user_id', 'allergen_id')
)

preference = Table(
    'preference',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('product_id', Integer, ForeignKey('product.id'), nullable=False),
    Column('max_value', Integer, nullable=False),
)

profile_preference = Table(
    'profile_preference',
    metadata,
    Column('user_id', UUID, ForeignKey(User.id), primary_key=True),
    Column('preference_id', Integer, ForeignKey('preference.id'), primary_key=True),
    Column('value', Integer, nullable=False),
    PrimaryKeyConstraint('user_id', 'preference_id')
)

profile_data = Table(
    'profile_data',
    metadata,
    Column('user_id', UUID, ForeignKey(User.id), primary_key=True),
    Column('text_preference', String(255)),
    Column('evaluation', Float, default=0.0),
)
