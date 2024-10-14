from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from src.auth.models import role
from src.auth.schemas import RoleCreate, RoleUpdate, RoleRead


# 1. Create a new role
async def create_role(role_data: RoleCreate, db: AsyncSession) -> RoleRead:
    try:
        # Insert a new role into the database
        new_role_stmt = role.insert().values(
            name=role_data.name,
            permissions=role_data.permissions
        ).returning(role.c.id, role.c.name, role.c.permissions)

        result = await db.execute(new_role_stmt)
        await db.commit()

        # Return the created role data
        created_role = result.fetchone()
        return RoleRead(
            id=created_role.id,
            name=created_role.name,
            permissions=created_role.permissions
        )

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating role: {e}")


# 2. Get all roles
async def get_all_roles(db: AsyncSession) -> List[RoleRead]:
    try:
        # Fetch all roles
        stmt = select(role.c.id, role.c.name, role.c.permissions)
        result = await db.execute(stmt)
        roles = result.fetchall()

        # Return list of RoleRead
        return [RoleRead(id=r.id, name=r.name, permissions=r.permissions) for r in roles]

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching roles: {e}")


# 3. Get a role by ID
async def get_role_by_id(role_id: int, db: AsyncSession) -> RoleRead:
    try:
        # Fetch the role by ID
        stmt = select(role.c.id, role.c.name, role.c.permissions).where(role.c.id == role_id)
        result = await db.execute(stmt)
        role_data = result.fetchone()

        if not role_data:
            raise HTTPException(status_code=404, detail="Role not found")

        # Return the role as RoleRead
        return RoleRead(id=role_data.id, name=role_data.name, permissions=role_data.permissions)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching role: {e}")


# 4. Update an existing role
async def update_role(role_id: int, role_data: RoleUpdate, db: AsyncSession) -> RoleRead:
    try:
        # Prepare the update statement
        update_stmt = update(role).where(role.c.id == role_id)

        # Update only provided fields
        if role_data.name is not None:
            update_stmt = update_stmt.values(name=role_data.name)
        if role_data.permissions is not None:
            update_stmt = update_stmt.values(permissions=role_data.permissions)

        result = await db.execute(update_stmt)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Role not found")

        # Return the updated role
        return await get_role_by_id(role_id, db)

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating role: {e}")
