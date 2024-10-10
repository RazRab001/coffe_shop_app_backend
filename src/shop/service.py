from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, delete, update

from src.product.model import shop_product
from src.shop.schema import CreatingShop, GettingShop
from src.shop.model import shop


async def create_shop(shop_data: CreatingShop, db: AsyncSession) -> Optional[GettingShop]:
    try:
        stmt = insert(shop).values(name=shop_data.name).returning(shop.c.id, shop.c.name)
        result = await db.execute(stmt)
        await db.commit()

        shop_row = result.fetchone()

        if shop_row:
            return GettingShop(id=shop_row.id, name=shop_row.name)

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Creation shop error: {e}")
        raise e


async def delete_shop(shop_id: int, db: AsyncSession) -> bool:
    try:
        await db.execute(
            update(shop_product).where(shop_product.c.shop_id == shop_id).values(shop_id=None)
        )

        stmt = delete(shop).where(shop.c.id == shop_id)
        result = await db.execute(stmt)
        await db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Deleting shop error: {e}")
        raise e
