from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from src.dependencies import get_db
from src.shop.schema import GettingShop, CreatingShop
from src.shop.service import create_shop, delete_shop

router = APIRouter(
    prefix="/shop",
)


@router.post("/", response_model=GettingShop, status_code=status.HTTP_201_CREATED)
async def create_new_shop(shop: CreatingShop, db: AsyncSession = Depends(get_db)) -> GettingShop:
    try:
        created_shop = await create_shop(shop, db)
        if not created_shop:
            raise HTTPException(status_code=400, detail="Failed to create shop")
        return created_shop
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_shop(shop_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await delete_shop(shop_id, db)
