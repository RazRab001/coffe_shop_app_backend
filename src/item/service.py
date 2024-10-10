from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, update, delete

from src.comment.service import get_comments_for_item, delete_comment
from src.item.model import item, ingredient
from src.item.schema import ItemFields, AddingIngredient, GettingItem, GettingIngredientValueForItem
from src.product.service import GettingProduct


async def create_item(data: ItemFields, db: AsyncSession) -> GettingItem:
    from src.product.service import get_product_by_id

    new_item = item.insert().values(
        title=data.title,
        description=data.description
    )

    try:
        result = await db.execute(new_item)
        await db.commit()

        item_id = result.inserted_primary_key[0]

        ingredients = []
        total_cost: float = 0.0

        if data.ingredients:
            for ing in data.ingredients:
                await add_ingredient(ing, item_id, db)
                product: GettingProduct = await get_product_by_id(ing.product_id, db)
                ingredient_cost: float = product.unit_cost * ing.value
                total_cost += ingredient_cost

                ingredients.append({
                    "product_id": product.id,
                    "name": product.name,
                    "value": ing.value,
                    "value_type": product.value_type,
                    "cost": ingredient_cost
                })

        return GettingItem(
            id=item_id,
            title=data.title,
            description=data.description,
            ingredients=ingredients,
            cost=total_cost
        )

    except IntegrityError as e:
        await db.rollback()
        raise e  # Прокидываем исключение наверх


async def get_all_active_items(db: AsyncSession) -> Optional[List[GettingItem]]:
    try:
        result = await db.execute(
            select(
                item.c.id,
                item.c.title,
                item.c.description,
                item.c.is_active
            ).where(item.c.is_active == True)
        )

        rows = result.fetchall()
        if not rows:
            return None

        active_items = [
            GettingItem(
                id=row.id,
                title=row.title,
                description=row.description,
                is_active=row.is_active
            )
            for row in rows
        ]

        return active_items

    except SQLAlchemyError as e:
        print(f"Error occurred while fetching active items: {e}")
        raise e  # Прокидываем исключение наверх


async def add_ingredient(ing: AddingIngredient, item_id: int, db: AsyncSession):
    try:
        new_ingredient = ingredient.insert().values(
            product_id=ing.product_id,
            value=ing.value,
            item_id=item_id
        )
        await db.execute(new_ingredient)
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while adding ingredient: {e}")
        raise e  # Прокидываем исключение наверх


async def update_ingredient(ingredient_id: int, value: float, db: AsyncSession):
    try:
        update_stmt = (
            update(ingredient)
            .where(ingredient.c.id == ingredient_id)
            .values(value=value)
        )
        await db.execute(update_stmt)
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while updating ingredient: {e}")
        raise e  # Прокидываем исключение наверх


async def delete_ingredient(ingredient_id: int, db: AsyncSession):
    try:
        delete_stmt = delete(ingredient).where(ingredient.c.id == ingredient_id)
        await db.execute(delete_stmt)
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while deleting ingredient: {e}")
        raise e  # Прокидываем исключение наверх


async def get_item_ids_by_product(product_id: int, db: AsyncSession) -> Optional[List[GettingIngredientValueForItem]]:
    try:
        query = await db.execute(
            select(
                ingredient.c.item_id,
                ingredient.c.value,
            ).where(ingredient.c.product_id == product_id)
        )

        rows = query.fetchall()
        item_ids = [
            GettingIngredientValueForItem(item_id=row.item_id, value=row.value)
            for row in rows
        ]

        return item_ids

    except SQLAlchemyError as e:
        print(f"Error occurred while fetching item IDs by product ID: {e}")
        raise e  # Прокидываем исключение наверх


async def set_activation_state(item_id: int, state: bool, db: AsyncSession) -> Optional[int]:
    try:
        update_stmt = (
            update(item)
            .where(item.c.id == item_id)
            .values(is_active=state)
        )

        await db.execute(update_stmt)
        await db.commit()

        return item_id
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while updating activation state: {e}")
        raise e  # Прокидываем исключение наверх


async def change_items_state_for_product(product_id: int, exist_product_value: float, db: AsyncSession):
    try:
        items_with_product = await get_item_ids_by_product(product_id, db)

        if not items_with_product:
            print(f"No items found for product_id: {product_id}")
            return

        for item in items_with_product:
            new_state = exist_product_value >= item.value
            await set_activation_state(item.item_id, new_state, db)

        await db.commit()

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while changing item states for product_id {product_id}: {e}")
        raise e  # Прокидываем исключение наверх


async def get_item_by_id(item_id: int, db: AsyncSession) -> GettingItem:
    try:
        # Выполняем запрос к базе данных для получения элемента по ID
        result = await db.execute(
            select(
                item.c.id,
                item.c.title,
                item.c.description,
                item.c.is_active
            ).where(item.c.id == item_id)
        )

        # Получаем первую строку результата
        row = result.fetchone()

        # Если элемент не найден, можно бросить исключение
        if row is None:
            raise ValueError(f"Item with ID {item_id} not found.")

        # Возвращаем объект GettingItem
        return GettingItem(
            id=row.id,
            title=row.title,
            description=row.description,
            is_active=row.is_active
        )

    except SQLAlchemyError as e:
        print(f"Error occurred while fetching item by ID: {e}")
        raise e  # Прокидываем исключение наверх


async def update_item(item_id: int, data: ItemFields, db: AsyncSession) -> GettingItem:
    # Получаем текущие ингредиенты для данного item_id
    existing_ingredients = await get_item_ids_by_product(item_id, db)

    # Создаем множество ID существующих ингредиентов для удобства поиска
    existing_ingredient_ids = {ing.product_id for ing in existing_ingredients}

    # Обновляем основной item
    try:
        update_stmt = (
            update(item)
            .where(item.c.id == item_id)
            .values(
                title=data.title,
                description=data.description
            )
        )
        await db.execute(update_stmt)

        # Обновляем ингредиенты
        for ing in data.ingredients:
            if ing.product_id in existing_ingredient_ids:
                await update_ingredient(ing.product_id, ing.value, db)
            else:
                await add_ingredient(ing, item_id, db)

        # Удаляем ингредиенты, которые отсутствуют в новом списке
        for existing_ing in existing_ingredients:
            if existing_ing.product_id not in {ing.product_id for ing in data.ingredients}:
                await delete_ingredient(existing_ing.product_id, db)

        await db.commit()
        return await get_item_by_id(item_id, db)

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while updating item: {e}")
        raise e  # Прокидываем исключение наверх


async def delete_item(item_id: int, db: AsyncSession) -> None:
    try:
        # Retrieve and delete all ingredients associated with the item
        stmt = select(ingredient.c.id).where(ingredient.c.item_id == item_id)
        ingredients_result = await db.execute(stmt)
        ingredient_ids = [row.id for row in ingredients_result.fetchall()]

        for ingredient_id in ingredient_ids:
            await delete_ingredient(ingredient_id, db)

        # Retrieve and delete all comments associated with the item
        comments = await get_comments_for_item(item_id, db)
        for comment in comments:
            await delete_comment(comment.id, db)

        # Delete the item itself
        delete_stmt = delete(item).where(item.c.id == item_id)
        await db.execute(delete_stmt)
        await db.commit()

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while deleting item and related data: {e}")
        raise e

