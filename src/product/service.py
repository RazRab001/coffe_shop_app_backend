from datetime import datetime
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert

from src.allergen.schema import GettingAllergen
from src.product.model import product, product_value_type, shop_product, allergen_product
from src.product.schema import CreationProduct, GettingProduct, AddingProduct
from src.allergen.model import allergen
from src.allergen.service import get_allergens_by_ids


async def create_new_product(data: CreationProduct, db: AsyncSession) -> Optional[GettingProduct]:
    try:
        # Get or create the value type
        value_type_id = await get_or_create_value_type(data.value_type, db)

        # Insert the new product
        new_product_stmt = insert(product).values(
            name=data.title,
            value_type_id=value_type_id,
        )
        result = await db.execute(new_product_stmt)
        product_id = result.inserted_primary_key[0]

        # Insert allergens for the product if provided
        if data.allergens:
            allergen_product_stmt = insert(allergen_product).values([
                {"allergen_id": allergen_id, "product_id": product_id} for allergen_id in data.allergens
            ])
            await db.execute(allergen_product_stmt)

        # Commit the transaction
        await db.commit()
        allergen_names = await get_allergen_names_by_ids(data.allergens, db) if data.allergens else []
        print(allergen_names)
        # Return the newly created product
        return GettingProduct(
            id=product_id,
            name=data.title,
            value=0,
            value_type=data.value_type,
            unit_cost=0,
            allergens=allergen_names
        )

    except SQLAlchemyError as e:
        # Rollback in case of error
        await db.rollback()
        print(f"Error occurred: {e}")
        raise e


async def get_or_create_value_type(value_type: str, db: AsyncSession) -> int:
    try:
        query = await db.execute(select(product_value_type).filter_by(name=value_type))
        existing_value_type = query.scalar()

        if existing_value_type:
            return existing_value_type
        else:
            new_value_type_stmt = insert(product_value_type).values(name=value_type)
            result = await db.execute(new_value_type_stmt)
            await db.commit()
            return result.inserted_primary_key[0]

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while fetching/creating value type: {e}")
        raise e


async def get_product_by_id(id: int, db: AsyncSession) -> Optional[GettingProduct]:
    try:
        # Query for product details
        query = await db.execute(
            select(
                product.c.id,
                product.c.name,
                product.c.value,
                product_value_type.c.name.label('value_type'),
                product.c.cost_per_one
            ).join(
                product_value_type, product.c.value_type_id == product_value_type.c.id
            ).filter(product.c.id == id)
        )

        product_data = query.first()

        if product_data:
            # Query for allergens associated with the product
            allergen_query = await db.execute(
                select(allergen.c.id, allergen.c.name)
                .join(allergen_product, allergen.c.id == allergen_product.c.allergen_id)
                .filter(allergen_product.c.product_id == id)
            )

            allergens = allergen_query.fetchall()
            allergen_names = [allergen.name for allergen in allergens]

            return GettingProduct(
                id=product_data.id,
                name=product_data.name,
                value=product_data.value,
                value_type=product_data.value_type,
                unit_cost=product_data.cost_per_one,
                allergens=allergen_names
            )
        else:
            raise ValueError(f"Product with ID {id} not found.")

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while fetching product by id: {e}")
        raise e


async def get_allergen_names_by_ids(allergen_ids: List[int], db: AsyncSession) -> List[str]:
    allergens: List[GettingAllergen] = await get_allergens_by_ids(allergen_ids, db)
    return [al_gen.name for al_gen in allergens]


async def add_portion_of_exist_product(product_id: int, data: AddingProduct, db: AsyncSession) -> Optional[GettingProduct]:
    from src.item.service import change_items_state_for_product

    try:
        existing_product = await get_product_by_id(product_id, db)

        if not existing_product:
            print(f"Product with id {product_id} not found")
            raise ValueError(f"Product with ID {product_id} not found.")

        new_value = existing_product.value + data.value

        new_unit_cost = (
            (existing_product.value * existing_product.unit_cost) +
            (data.value * data.unit_cost)
        ) / new_value

        update_product_stmt = update(product).where(product.c.id == product_id).values(
            value=new_value,
            cost_per_one=new_unit_cost
        )
        await db.execute(update_product_stmt)

        if data.shop_id:
            new_shop_product_stmt = insert(shop_product).values(
                shop_id=data.shop_id,
                product_id=product_id,
                added_at=datetime.now()
            )
            await db.execute(new_shop_product_stmt)

        await db.commit()

        await change_items_state_for_product(product_id, new_value, db)

        return await get_product_by_id(product_id, db)

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while adding portion of product: {e}")
        raise e


async def remove_portion_of_exist_product(product_id: int, value: float, db: AsyncSession) -> Optional[GettingProduct]:
    from src.item.service import change_items_state_for_product

    try:
        existing_product = await get_product_by_id(product_id, db)

        if not existing_product:
            print(f"Product with id {product_id} not found")
            raise ValueError(f"Product with ID {product_id} not found.")

        new_value = existing_product.value - value

        if new_value < 0:
            raise ValueError(f"Cannot remove more than available quantity. Current value: {existing_product.value}")

        update_product_stmt = update(product).where(product.c.id == product_id).values(
            value=new_value,
        )
        await db.execute(update_product_stmt)

        await db.commit()

        await change_items_state_for_product(product_id, new_value, db)
        return await get_product_by_id(product_id, db)

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while removing portion of product: {e}")
        raise e


async def get_all_products(db: AsyncSession) -> List[GettingProduct]:
    from src.allergen.model import allergen
    try:
        # Запрос на получение всех продуктов
        query = await db.execute(
            select(
                product.c.id,
                product.c.name,
                product.c.value,
                product_value_type.c.name.label('value_type'),
                product.c.cost_per_one
            ).join(
                product_value_type, product.c.value_type_id == product_value_type.c.id
            )
        )

        products = query.fetchall()

        all_products = []

        # Перебираем каждый продукт и получаем для него аллергены
        for product_data in products:
            # Запрос на получение аллергенов для каждого продукта
            allergen_query = await db.execute(
                select(allergen.c.id, allergen.c.name)
                .join(allergen_product, allergen.c.id == allergen_product.c.allergen_id)
                .filter(allergen_product.c.product_id == product_data.id)
            )

            allergens = allergen_query.fetchall()
            allergen_names = [allergen.name for allergen in allergens]

            # Добавляем продукт в список
            all_products.append(GettingProduct(
                id=product_data.id,
                name=product_data.name,
                value=product_data.value,
                value_type=product_data.value_type,
                unit_cost=product_data.cost_per_one,
                allergens=allergen_names
            ))

        return all_products

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while fetching all products: {e}")
        raise e
