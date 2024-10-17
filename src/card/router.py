from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from src.auth.models import User
from src.dependencies import get_db, permission_dependency
from src.card.schema import CreatingCard, UpdatingCard, GettingCard
from src.card.service import create_card, update_card, get_card_by_id, get_card_by_phone, delete_card, get_card_by_user

router = APIRouter(
    prefix="/card",
)


@router.post("", response_model=GettingCard)
async def create_new_card(card: CreatingCard, db: AsyncSession = Depends(get_db),
                          user: User = Depends(permission_dependency())) -> GettingCard:
    check_user: User = await permission_dependency("create_card", goal_user_id=card.user_id)(user, db)

    created_allergen = await create_card(card, db)
    if not created_allergen:
        raise HTTPException(status_code=400, detail="Failed to create card")
    return created_allergen


@router.get("/id/{card_id}", response_model=GettingCard)
async def get_card_with_id(card_id: int, db: AsyncSession = Depends(get_db)) -> GettingCard:
    card = await get_card_by_id(card_id, db)
    if not card:
        raise HTTPException(status_code=400, detail="Failed to find card")
    return card


@router.get("/phone/{phone}", response_model=GettingCard)
async def get_card_with_phone_number(phone: str, db: AsyncSession = Depends(get_db)) -> GettingCard:
    card = await get_card_by_phone(phone, db)
    if not card:
        raise HTTPException(status_code=400, detail="Failed to find card")
    return card


@router.get("", response_model=GettingCard)
async def get_card_by_owner_id(db: AsyncSession = Depends(get_db), user: User = Depends(permission_dependency())) -> GettingCard:
    card = await get_card_by_user(user.id, db)
    if not card:
        raise HTTPException(status_code=400, detail="Failed to find card")
    return card


@router.put("/{card_id}", response_model=GettingCard)
async def update_card_data(card_id: int, card: UpdatingCard, db: AsyncSession = Depends(get_db),
                           user: User = Depends(permission_dependency())) -> GettingCard:
    existed_card = await get_card_by_id(card_id, db)
    check_user: User = await permission_dependency("update_card", goal_user_id=existed_card.user_id)(user, db)
    card = await update_card(card_id, card, db)
    if not card:
        raise HTTPException(status_code=400, detail="Failed to update card")
    return card


@router.put("", response_model=GettingCard)
async def update_card_data_by_user(card: UpdatingCard, db: AsyncSession = Depends(get_db),
                           user: User = Depends(permission_dependency())) -> GettingCard:
    existed_card = await get_card_by_user(user.id, db)
    card = await update_card(existed_card.id, card, db)
    if not card:
        raise HTTPException(status_code=400, detail="Failed to update card")
    return card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_card(card_id: int, db: AsyncSession = Depends(get_db),
                               user: User = Depends(permission_dependency())) -> None:
    card = await get_card_by_id(card_id, db)
    check_user: User = await permission_dependency("delete_card", goal_user_id=card.user_id)(user, db)
    await delete_card(card_id, db)
