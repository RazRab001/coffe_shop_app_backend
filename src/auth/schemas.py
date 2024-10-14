import uuid
from typing import Optional, List
from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    id: UUID
    email: str
    username: str
    role_id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    role_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    pass


class RoleCreate(BaseModel):
    name: str
    permissions: List[str]


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleRead(BaseModel):
    id: int
    name: str
    permissions: List[str]

    class Config:
        orm_mode = True
