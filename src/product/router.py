from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from src.auth.models import User
from src.dependencies import get_db, permission_dependency
from src.product.service import create_new_product, add_portion_of_exist_product, remove_portion_of_exist_product, get_product_by_id, get_all_products
from src.product.schema import GettingProduct, CreationProduct, AddingProduct, ReducingProduct

router = APIRouter(
    prefix="/product",
)


@router.post("", response_model=GettingProduct, status_code=status.HTTP_201_CREATED)
async def create_product(product: CreationProduct, db: AsyncSession = Depends(get_db),
                         user: User = Depends(permission_dependency("create_product"))) -> GettingProduct:
    created_product = await create_new_product(product, db)
    if not created_product:
        raise HTTPException(status_code=400, detail="Failed to create product")
    return created_product


@router.put("/add/{product_id}", response_model=GettingProduct)
async def add_product(product_id: int, product: AddingProduct, db: AsyncSession = Depends(get_db),
                      user: User = Depends(permission_dependency("change_product"))) -> GettingProduct:
    updated_product = await add_portion_of_exist_product(product_id, product, db)
    if not updated_product:
        raise HTTPException(status_code=400, detail="Failed to update product")
    return updated_product


@router.put("/reduce/{product_id}", response_model=GettingProduct)
async def reduce_product(product_id: int, product: ReducingProduct, db: AsyncSession = Depends(get_db),
                         user: User = Depends(permission_dependency("change_product"))) -> GettingProduct:
    updated_product = await remove_portion_of_exist_product(product_id, product.value, db)
    if not updated_product:
        raise HTTPException(status_code=400, detail="Failed to update product")
    return updated_product


@router.get("/{product_id}", response_model=GettingProduct)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)) -> GettingProduct:
    product = await get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=400, detail="Failed to get product")
    return product


@router.get("", response_model=List[GettingProduct])
async def get_products(db: AsyncSession = Depends(get_db)) -> list[GettingProduct]:
    return await get_all_products(db)
