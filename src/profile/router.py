from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from src.auth.models import User
from src.dependencies import get_db, permission_dependency
from src.profile.schema import UpdatingProfile, GettingProfile, CreatingPreference, GettingPreference
from src.profile.service import update_profile, create_preference, get_profile_by_id, get_preferences, delete_preference

router = APIRouter(
    prefix="/profile",
)


@router.put("/{user_id}", response_model=GettingProfile)
async def update_user_profile(user_id: UUID, profile: UpdatingProfile, db: AsyncSession = Depends(get_db),
                              user: User = Depends(permission_dependency())):
    check_user: User = await permission_dependency("update_profile", goal_user_id=user_id)(user, db)
    try:
        updated_profile = await update_profile(user_id, profile, db)
        return updated_profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/preference", response_model=GettingPreference)
async def add_preference(preference: CreatingPreference, db: AsyncSession = Depends(get_db),
                         user: User = Depends(permission_dependency("add_preference"))):
    try:
        created_preference = await create_preference(preference, db)
        return created_preference
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=GettingProfile)
async def get_user_profile(user_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        print(f"Looking for user with ID: {user_id}")
        profile = await get_profile_by_id(user_id, db)
        return profile
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/preferences", response_model=List[GettingPreference])
async def get_all_preferences(db: AsyncSession = Depends(get_db)):
    try:
        preferences = await get_preferences(db)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/preference/{preference_id}", status_code=204)
async def remove_preference(preference_id: int, db: AsyncSession = Depends(get_db),
                            user: User = Depends(permission_dependency("remove_preference"))):
    try:
        await delete_preference(preference_id, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
