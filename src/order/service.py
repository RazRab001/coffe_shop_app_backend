from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, update, delete

from src.item.service import get_item_by_id
from src.profile.service import get_profile_by_id
from src.product.service import get_product_by_id
from src.order.model import order, order_item, order_item_ingredient
from src.order.schema import CreatingOrder, OrderItem, OrderItemIngredient, GettingOrder


async def create_order(user_id: UUID, order_data: CreatingOrder, db: AsyncSession) -> GettingOrder:
    try:
        user = await get_profile_by_id(user_id, db)
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        total_cost = 0
        validated_items = []

        for order_item_data in order_data.items:
            item_info = await get_item_by_id(order_item_data.item_id, db)
            if not item_info:
                raise ValueError(f"Item with ID {order_item_data.item_id} not found.")

            item_cost = item_info.cost * order_item_data.count
            for ingredient_data in order_item_data.ingredients:
                ingredient_product = await get_product_by_id(ingredient_data.product_id, db)
                if not ingredient_product:
                    raise ValueError(f"Product with ID {ingredient_data.product_id} not found as ingredient.")

                item_cost += ingredient_product.cost * ingredient_data.value

            total_cost += item_cost
            validated_items.append((order_item_data, item_info))

        new_order_stmt = order.insert().values(
            user_id=user_id,
            cost=total_cost,
            date=datetime.utcnow(),
            comment=order_data.comment
        )
        result = await db.execute(new_order_stmt)
        await db.commit()

        order_id = result.inserted_primary_key[0]

        for order_item_data, item_info in validated_items:
            new_order_item_stmt = order_item.insert().values(
                order_id=order_id,
                item_id=order_item_data.item_id,
                count=order_item_data.count
            )
            await db.execute(new_order_item_stmt)

            for ingredient_data in order_item_data.ingredients:
                await db.execute(
                    order_item_ingredient.insert().values(
                        order_item_id=order_item_data.item_id,
                        product_id=ingredient_data.product_id,
                        value=ingredient_data.value
                    )
                )

        await db.commit()

        return await get_order_by_id(order_id, db)

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while creating order: {e}")
        raise e


async def get_user_orders(user_id: UUID, db: AsyncSession) -> List[GettingOrder]:
    try:
        stmt = select(order).where(order.c.user_id == user_id)
        result = await db.execute(stmt)
        orders = result.fetchall()

        user_orders = []
        for order_row in orders:
            order_id = order_row.id
            order_items = await db.execute(
                select(order_item).where(order_item.c.order_id == order_id)
            )

            order_items_info = []
            for order_item_row in order_items:
                item_info = await get_item_by_id(order_item_row.item_id, db)
                order_items_info.append(item_info)

            user_orders.append(
                GettingOrder(
                    id=order_row.id,
                    user_id=order_row.user_id,
                    date=order_row.date,
                    cost=order_row.cost,
                    items=order_items_info
                )
            )

        return user_orders

    except SQLAlchemyError as e:
        print(f"Error occurred while fetching user orders: {e}")
        raise e


async def get_order_by_id(order_id: int, db: AsyncSession) -> GettingOrder:
    try:
        stmt = select(order).where(order.c.id == order_id)
        result = await db.execute(stmt)
        order_row = result.fetchone()

        if not order_row:
            raise ValueError(f"Order with ID {order_id} not found.")

        order_items = await db.execute(
            select(order_item).where(order_item.c.order_id == order_id)
        )
        order_items_info = []

        for order_item_row in order_items:
            item_info = await get_item_by_id(order_item_row.item_id, db)
            order_items_info.append(item_info)

        return GettingOrder(
            id=order_row.id,
            user_id=order_row.user_id,
            date=order_row.date,
            cost=order_row.cost,
            items=order_items_info
        )

    except SQLAlchemyError as e:
        print(f"Error occurred while fetching order by ID: {e}")
        raise e
