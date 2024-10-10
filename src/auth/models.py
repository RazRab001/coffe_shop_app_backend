from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import (JSON, TIMESTAMP, Boolean, Column, ForeignKey, Integer,
                        String, Table, UUID)

from src.database import Base, metadata

role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON),
    extend_existing=True
)


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "profile"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID, primary_key=True, unique=True, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    username = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey(role.c.id))
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
