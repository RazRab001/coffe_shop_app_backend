from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_session
from src.auth.models import User, role
from src.auth.base_config import current_active_user


async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session


def permission_dependency(permission_name: str):
    async def _check_permission(
            user: User = Depends(current_active_user),
            db: AsyncSession = Depends(get_db)
    ) -> User:
        return await check_permission(permission_name, user, db)

    return _check_permission


async def check_permission(permission_name: str,
                           user: User = Depends(current_active_user),
                           db: AsyncSession = Depends(get_db)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Retrieve the user by their ID
    user_stmt = select(User).filter(User.id == user.id)
    user_result = await db.execute(user_stmt)
    user_data = user_result.scalar_one_or_none()

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Retrieve the role using role_id from user_data
    role_stmt = select(role).filter(role.c.id == user_data.role_id)
    role_result = await db.execute(role_stmt)
    role_data = role_result.scalar_one_or_none()

    if not role_data:
        raise HTTPException(status_code=404, detail="Role not found")

    # Extract permissions from the role's JSON field
    role_permissions = role_data.permissions or []

    # Check if the required permission exists in the role's permissions
    if permission_name not in role_permissions:
        raise HTTPException(status_code=403, detail="Access forbidden: insufficient permissions")

    return user_data
