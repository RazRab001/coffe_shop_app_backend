from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from src.dependencies import get_db
from src.allergen.schema import CreatingAllergen, GettingAllergen
from src.allergen.service import create_allergen, delete_allergen, get_all, get_by_id

router = APIRouter(
    prefix="/allergen",
)


@router.post("", response_model=GettingAllergen)
async def create_new_allergen(allergen: CreatingAllergen, db: AsyncSession = Depends(get_db)) -> GettingAllergen:
    created_allergen = await create_allergen(allergen, db)
    if not created_allergen:
        raise HTTPException(status_code=400, detail="Failed to create item")
    return created_allergen


@router.get("", response_model=List[GettingAllergen])
async def get_allergens(db: AsyncSession = Depends(get_db)) -> List[GettingAllergen]:
    try:
        return await get_all(db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.get("/{allergen_id}", response_model=GettingAllergen)
async def get_one_allergen(allergen_id: int, db: AsyncSession = Depends(get_db)) -> GettingAllergen:
    allergen = await get_by_id(allergen_id, db)
    if not allergen:
        raise HTTPException(status_code=400, detail="Failed to update item")
    return allergen


@router.delete("/{allergen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_allergen(allergen_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await delete_allergen(allergen_id, db)
