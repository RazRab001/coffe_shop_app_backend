from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, delete

from src.allergen.schema import CreatingAllergen, GettingAllergen
from src.allergen.model import allergen  # Assuming you have the allergen table defined in models
from typing import Optional, List


# Function to create a new allergen in the database
async def create_allergen(allergen_data: CreatingAllergen, db: AsyncSession) -> Optional[GettingAllergen]:
    new_allergen = allergen.insert().values(name=allergen_data.name)
    try:
        # Insert allergen into the database
        await db.execute(new_allergen)
        await db.commit()

        # Fetch the newly created allergen to return
        query = select(allergen).where(allergen.c.name == allergen_data.name)
        result = await db.execute(query)
        created_allergen = result.fetchone()

        if created_allergen:
            return GettingAllergen(id=created_allergen.id, name=created_allergen.name)

    except IntegrityError as e:
        await db.rollback()
        raise e  # Propagate the exception to the caller

    except SQLAlchemyError as e:
        await db.rollback()
        raise e  # Propagate the exception to the caller


# Function to delete an allergen from the database
async def delete_allergen(allergen_id: int, db: AsyncSession) -> None:
    query = delete(allergen).where(allergen.c.id == allergen_id)
    try:
        result = await db.execute(query)
        if result.rowcount > 0:
            await db.commit()
        else:
            await db.rollback()

    except SQLAlchemyError as e:
        await db.rollback()
        raise e  # Propagate the exception to the caller


# Function to get an allergen by ID
async def get_by_id(allergen_id: int, db: AsyncSession) -> Optional[GettingAllergen]:
    query = select(allergen).where(allergen.c.id == allergen_id)
    try:
        result = await db.execute(query)
        found_allergen = result.fetchone()

        if found_allergen:
            return GettingAllergen(id=found_allergen.id, name=found_allergen.name)
        return None

    except SQLAlchemyError as e:
        raise e  # Propagate the exception to the caller


# Function to get all allergens
async def get_all(db: AsyncSession) -> List[GettingAllergen]:
    query = select(allergen)
    try:
        result = await db.execute(query)
        allergens = result.fetchall()

        return [GettingAllergen(id=allergen.id, name=allergen.name) for allergen in allergens]

    except SQLAlchemyError as e:
        raise e  # Propagate the exception to the caller


async def get_allergens_by_ids(allergen_ids: List[int], db: AsyncSession) -> List[GettingAllergen]:
    query = select(allergen).where(allergen.c.id.in_(allergen_ids))  # Correctly use in_ for SQLAlchemy
    try:
        result = await db.execute(query)
        found_allergens = result.fetchall()  # Fetch all rows that match the query
        print(found_allergens)
        # Convert the result to a list of GettingAllergen objects
        return [GettingAllergen(id=row.id, name=row.name) for row in found_allergens]

    except SQLAlchemyError as e:
        raise e  # Propagate the error
