from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.dependencies import get_db
from src.product.service import create_new_product, add_portion_of_exist_product, remove_portion_of_exist_product
from src.product.schema import GettingProduct, CreationProduct, AddingProduct, ReducingProduct

router = APIRouter(
    prefix="/product",
)


@router.post("", response_model=GettingProduct)
async def create_product(product: CreationProduct, db: AsyncSession = Depends(get_db)) -> GettingProduct:
    created_product = await create_new_product(product, db)
    if not created_product:
        raise HTTPException(status_code=400, detail="Failed to create product")
    return created_product


@router.put("/add/{product_id}", response_model=GettingProduct)
async def add_product(product_id: int, product: AddingProduct, db: AsyncSession = Depends(get_db)) -> GettingProduct:
    updated_product = await add_portion_of_exist_product(product_id, product, db)
    if not updated_product:
        raise HTTPException(status_code=400, detail="Failed to update product")
    return updated_product


@router.put("/reduce/{product_id}", response_model=GettingProduct)
async def reduce_product(product_id: int, product: ReducingProduct, db: AsyncSession = Depends(get_db)) -> GettingProduct:
    updated_product = await remove_portion_of_exist_product(product_id, product.value, db)
    if not updated_product:
        raise HTTPException(status_code=400, detail="Failed to update product")
    return updated_product
