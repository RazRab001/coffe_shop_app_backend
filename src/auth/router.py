from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies import get_db
from src.auth.service import create_role, get_all_roles, get_role_by_id, update_role
from src.auth.schemas import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(prefix="/role")


@router.post("/", response_model=RoleRead)
async def create_new_role(role_data: RoleCreate, db: AsyncSession = Depends(get_db)):
    return await create_role(role_data, db)


@router.get("/", response_model=List[RoleRead])
async def list_all_roles(db: AsyncSession = Depends(get_db)):
    return await get_all_roles(db)


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    return await get_role_by_id(role_id, db)


@router.put("/{role_id}", response_model=RoleRead)
async def modify_role(role_id: int, role_data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    return await update_role(role_id, role_data, db)
