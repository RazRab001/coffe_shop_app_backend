from src.product.model import product
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, update, delete, insert

from src.comment.service import get_comments_for_item, delete_comment
from src.item.model import item, ingredient
from src.item.schema import ItemFields, AddingIngredient, GettingItem, GettingIngredientValueForItem, GettingIngredients
from src.product.service import GettingProduct, get_product_by_id
from src.product.model import product_value_type


async def create_item(data: ItemFields, db: AsyncSession) -> GettingItem:
    from src.product.service import get_product_by_id

    try:
        # Insert new item into the database with RETURNING to get the full record back
        stmt = insert(item).values(
            title=data.title,
            description=data.description,
            cost=data.cost,  # Initially cost can be passed or updated later based on ingredients
            actualise_cost=data.actualise_cost,
            is_active=True  # Assuming a new item is active by default
        ).returning(
            item.c.id, item.c.title, item.c.description, item.c.cost, item.c.actualise_cost, item.c.is_active
        )

        # Executing the insert statement
        result = await db.execute(stmt)
        await db.commit()

        # Extracting the returned row
        new_item_data = result.fetchone()
        item_id = new_item_data.id

        ingredients = []
        total_cost: float = 0.0

        # Processing each ingredient if provided
        if data.ingredients:
            for ing in data.ingredients:
                # Adding the ingredient to the database
                await add_ingredient(ing, item_id, db)

                # Fetching product details for the given product_id
                product: GettingProduct = await get_product_by_id(ing.product_id, db)

                # Calculating the cost for the ingredient
                ingredient_cost: float = product.unit_cost * ing.value
                total_cost += ingredient_cost

                # Storing the ingredient details
                ingredients.append({
                    "product_id": product.id,
                    "name": product.name,
                    "value": ing.value,
                    "value_type": product.value_type,
                    "cost": ingredient_cost
                })

        # If 'actualise_cost' is True, update the cost with the total cost of ingredients
        if data.actualise_cost:
            await db.execute(
                item.update().where(item.c.id == item_id).values(cost=total_cost)
            )
            await db.commit()

        # Return the newly created item data along with the ingredients
        return GettingItem(
            id=new_item_data.id,
            title=new_item_data.title,
            description=new_item_data.description,
            ingredients=ingredients,
            cost=total_cost if data.actualise_cost else new_item_data.cost,
            actualise_cost=new_item_data.actualise_cost,
            is_active=new_item_data.is_active
        )

    except IntegrityError as e:
        # Rollback the transaction in case of an error
        await db.rollback()
        raise e


async def get_ingredients_for_item(item_id: int, db: AsyncSession) -> List[GettingIngredients]:
    try:
        # Получаем product_id, value, name и value_type из таблицы ingredient, если они есть
        ingredient_stmt = (
            select(
                ingredient.c.product_id,
                ingredient.c.value,
                ingredient.c.name,
                ingredient.c.value_type_id,
                product.c.name.label("product_name"),
                product_value_type.c.name.label("product_value_type"),
                product.c.cost_per_one.label("product_cost")
            )
            .join(product, ingredient.c.product_id == product.c.id, isouter=True)
            .join(product_value_type, product.c.value_type_id == product_value_type.c.id, isouter=True)
            .where(ingredient.c.item_id == item_id)
        )

        ingredient_result = await db.execute(ingredient_stmt)
        ingredient_rows = ingredient_result.fetchall()

        # Формируем список ингредиентов
        ingredients_list = []
        for row in ingredient_rows:
            # Если данные есть в ingredient, используем их, иначе fallback на product или дефолтные значения
            ingredients_list.append(
                GettingIngredients(
                    product_id=row.product_id,
                    name=row.name if row.name else (row.product_name or ''),  # Имя из ingredient или product
                    value=row.value,  # Обязательно берем значение из ingredient
                    value_type=row.product_value_type if row.value_type_id is None else row.value_type_id,  # value_type из ingredient или product
                    cost=row.product_cost if row.product_cost is not None else 0.0  # Цена из product или дефолт
                )
            )

        return ingredients_list

    except SQLAlchemyError as e:
        print(f"Error occurred while fetching ingredients for item {item_id}: {e}")
        raise e


async def get_all_active_items(db: AsyncSession) -> Optional[List[GettingItem]]:
    try:
        result = await db.execute(
            select(
                item.c.id,
                item.c.title,
                item.c.description,
                item.c.actualise_cost,
                item.c.is_active,
                item.c.cost
            ).where(item.c.is_active == True)
        )

        rows = result.fetchall()
        if not rows:
            return None

        active_items = []

        for row in rows:
            if row.actualise_cost:
                total_cost = await calculate_total_cost(row.id, db)
                await db.execute(
                    update(item).where(item.c.id == row.id).values(cost=total_cost)
                )
                await db.commit()
            else:
                total_cost = row.cost

            ingredients_list = await get_ingredients_for_item(row.id, db)

            active_items.append(
                GettingItem(
                    id=row.id,
                    title=row.title,
                    description=row.description,
                    ingredients=ingredients_list,
                    cost=total_cost,
                    actualise_cost=row.actualise_cost,
                    is_active=row.is_active
                )
            )

        return active_items

    except SQLAlchemyError as e:
        print(f"Error occurred while fetching active items: {e}")
        raise e


async def add_ingredient(ing: AddingIngredient, item_id: int, db: AsyncSession):
    try:
        if ing.product_id:
            product = await get_product_by_id(ing.product_id, db)
            if not product:
                raise ValueError(f"Product with id {ing.product_id} does not exist.")
        else:
            product = None

        if not ing.product_id and (not ing.name or not ing.value_type):
            raise ValueError("Either product_id or both name and value_type must be provided.")

        new_ingredient = ingredient.insert().values(
            product_id=ing.product_id,
            value=ing.value,
            item_id=item_id,
            value_type_id=ing.value_type.value if ing.value_type else (product.value_type if product else None),
            name=ing.name if ing.name else (product.name if product else None)
        )

        await db.execute(new_ingredient)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while adding ingredient: {e}")
        raise e
    except ValueError as ve:
        print(f"Validation error: {ve}")
        raise ve


async def update_ingredient(ingredient_id: int, ing: AddingIngredient, db: AsyncSession):
    try:
        update_stmt = (
            update(ingredient)
            .where(ingredient.c.id == ingredient_id)
            .values(
                product_id=ing.product_id,
                value=ing.value,
                name=ing.name,
                value_type_id=ing.value_type.value if ing.value_type else None
            )
        )
        await db.execute(update_stmt)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while updating ingredient: {e}")
        raise e


async def delete_ingredient(ingredient_id: int, db: AsyncSession):
    try:
        delete_stmt = delete(ingredient).where(ingredient.c.id == ingredient_id)
        await db.execute(delete_stmt)
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while deleting ingredient: {e}")
        raise e


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
        raise e


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
        raise e


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
        raise e


async def get_item_by_id(item_id: int, db: AsyncSession) -> GettingItem:
    try:
        result = await db.execute(
            select(
                item.c.id,
                item.c.title,
                item.c.description,
                item.c.is_active,
                item.c.actualise_cost,
                item.c.cost
            ).where(item.c.id == item_id)
        )

        row = result.fetchone()
        if row is None:
            raise ValueError(f"Item with ID {item_id} not found.")

        if row.actualise_cost:
            total_cost = await calculate_total_cost(item_id, db)
            await db.execute(
                update(item).where(item.c.id == item_id).values(cost=total_cost)
            )
            await db.commit()
        else:
            total_cost = row.cost

        ingredients_list = get_ingredients_for_item(item_id, db)

        return GettingItem(
            id=row.id,
            title=row.title,
            description=row.description,
            ingredients=ingredients_list,
            cost=total_cost,
            actualise_cost=row.actualise_cost,
            is_active=row.is_active
        )

    except SQLAlchemyError as e:
        print(f"Error occurred while fetching item by ID: {e}")
        raise e


async def update_item(item_id: int, data: ItemFields, db: AsyncSession) -> GettingItem:
    existing_ingredients = await get_item_ids_by_product(item_id, db)
    existing_ingredient_ids = {ing.product_id for ing in existing_ingredients}

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

        for ing in data.ingredients:
            if ing.product_id in existing_ingredient_ids:
                await update_ingredient(ing.product_id, ing.value, db)
            else:
                await add_ingredient(ing, item_id, db)

        for existing_ing in existing_ingredients:
            if existing_ing.product_id not in {ing.product_id for ing in data.ingredients}:
                await delete_ingredient(existing_ing.product_id, db)

        await db.commit()
        return await get_item_by_id(item_id, db)

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while updating item: {e}")
        raise e


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


async def calculate_total_cost(item_id: int, db: AsyncSession) -> float:
    try:
        ingredient_stmt = (
            select(
                ingredient.c.product_id,
                ingredient.c.value,
                product.c.cost_per_one.label('product_cost')
            )
            .join(product, ingredient.c.product_id == product.c.id, isouter=True)
            .where(ingredient.c.item_id == item_id)
        )

        ingredient_result = await db.execute(ingredient_stmt)
        ingredients = ingredient_result.fetchall()

        # Вычисляем общую стоимость
        total_cost = sum(
            row.value * (row.product_cost or 0.0)  # Если стоимость не указана, берем 0
            for row in ingredients
        )

        return total_cost

    except SQLAlchemyError as e:
        print(f"Error occurred while calculating total cost for item {item_id}: {e}")
        raise e
