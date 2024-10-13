from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.dependencies import get_db
from src.order.schema import GettingOrder, CreatingOrder
from src.order.service import create_order, get_order_by_id, get_user_orders

from src.event.schema import UseAkcesForm
from src.event.service import use_akce

router = APIRouter(
    prefix="/order",
)


@router.post("", response_model=GettingOrder, status_code=status.HTTP_201_CREATED)
async def create_new_order(order: CreatingOrder, db: AsyncSession = Depends(get_db)) -> GettingOrder:
    created_order = await create_order(order, db)
    if not created_order:
        raise HTTPException(status_code=400, detail="Failed to create order")
    return created_order


@router.get("/{user_id}", response_model=List[GettingOrder])
async def get_user_all_orders(user_id: UUID, db: AsyncSession = Depends(get_db)) -> List[GettingOrder]:
    try:
        orders = await get_user_orders(user_id, db)
        if not orders:
            raise HTTPException(status_code=404, detail="No orders found for this user")
        return orders
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.get("/{order_id}/detail", response_model=GettingOrder)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)) -> GettingOrder:
    try:
        order = await get_order_by_id(order_id, db)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
        return order
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.put("", response_model=GettingOrder)
async def use_actions_for_order(data: UseAkcesForm, db: AsyncSession = Depends(get_db)) -> GettingOrder:
    akce_order = await use_akce(data, db)
    if not akce_order:
        raise HTTPException(status_code=400, detail="Failed to using akce with order")
    return akce_order
