from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from src.dependencies import get_db
from src.item.schema import ItemFields, GettingItem
from src.item.service import create_item, get_all_active_items, update_item, delete_item, get_item_by_id

router = APIRouter(
    prefix="/item",
)


@router.post("", response_model=GettingItem, status_code=status.HTTP_201_CREATED)
async def create_new_item(item: ItemFields, db: AsyncSession = Depends(get_db)) -> GettingItem:
    created_item = await create_item(item, db)
    if not created_item:
        raise HTTPException(status_code=400, detail="Failed to create item")
    return created_item


@router.get("", response_model=List[GettingItem])
async def get_items(db: AsyncSession = Depends(get_db)) -> List[GettingItem]:
    try:
        return await get_all_active_items(db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.get("/{item_id}", response_model=GettingItem)
async def get_by_id(item_id: int, db: AsyncSession = Depends(get_db)) -> GettingItem:
    try:
        return await get_item_by_id(item_id, db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.put("/{item_id}", response_model=GettingItem)
async def update_one_item(item_id: int, item: ItemFields, db: AsyncSession = Depends(get_db)) -> GettingItem:
    updated_item = await update_item(item_id, item, db)
    if not updated_item:
        raise HTTPException(status_code=400, detail="Failed to update item")
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_item(item_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await delete_item(item_id, db)
