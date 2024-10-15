from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, update, delete

from src.allergen.schema import GettingAllergen
from src.product.schema import GettingProduct
from src.auth.models import User
from src.item.model import item, ingredient
from src.profile.model import user_allergen, preference, profile_preference, profile_data
from src.profile.schema import UpdatingProfile, GettingProfile, CreatingPreference, GettingPreference, \
    GettingProfilePreference
from src.product.service import get_product_by_id
from src.allergen.service import get_by_id


async def update_profile(user_id: UUID, profile: UpdatingProfile, db: AsyncSession) -> GettingProfile:
    try:
        # Update basic profile info: username, phone
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(username=profile.username, phone=profile.phone.e164)
        )
        await db.execute(stmt)

        # Update text_preference in profile_data
        stmt = (
            update(profile_data)
            .where(profile_data.c.user_id == user_id)
            .values(text_preference=profile.text_preference)
        )
        await db.execute(stmt)

        # Update preferences
        for preference in profile.preferences:
            stmt = (
                update(profile_preference)
                .where(
                    profile_preference.c.user_id == user_id,
                    profile_preference.c.preference_id == preference.product_id
                )
                .values(value=preference.value)
            )
            await db.execute(stmt)

        # Update allergens (replace existing ones)
        stmt = delete(user_allergen).where(user_allergen.c.user_id == user_id)
        await db.execute(stmt)

        for allergen in profile.allergens:
            stmt = user_allergen.insert().values(user_id=user_id, allergen_id=allergen.allergen_id)
            await db.execute(stmt)

        await db.commit()

        return await get_profile_by_id(user_id, db)
    except IntegrityError as e:
        await db.rollback()
        raise e


async def change_evaluation(user_id: UUID, value: float, db: AsyncSession) -> None:
    try:
        stmt = (
            update(profile_data)
            .where(profile_data.c.user_id == user_id)
            .values(evaluation=value)
        )
        await db.execute(stmt)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise SQLAlchemyError(f"Error updating evaluation: {str(e)}")


async def create_preference(preference: CreatingPreference, db: AsyncSession) -> GettingPreference:
    try:
        existing_product = await get_product_by_id(preference.product_id, db)

        if not existing_product:
            print(f"Product with id {preference.product_id} not found")
            raise ValueError(f"Product with ID {preference.product_id} not found.")

        stmt = preference.insert().values(
            product_id=preference.product_id,
            max_value=preference.max_value
        )
        result = await db.execute(stmt)
        await db.commit()

        # Return the newly created preference
        return GettingPreference(
            product_id=preference.product_id,
            product_name=existing_product.name,
            max_value=preference.max_value
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def get_profile_by_id(user_id: UUID, db: AsyncSession) -> GettingProfile:
    try:
        # Query user basic info
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one()
        print(user.email)
        # Query preferences
        stmt = select(preference, profile_preference.c.value).where(
            profile_preference.c.user_id == user_id,
            profile_preference.c.preference_id == preference.c.id
        )
        pref_results = await db.execute(stmt)
        print(pref_results)
        preferences = []

        for row in pref_results:
            # Fetch the product information using the product_id
            existing_product = await get_product_by_id(row.preference.c.product_id, db)

            if not existing_product:
                print(f"Product with id {row.preference.c.product_id} not found")
                raise ValueError(f"Product with ID {row.preference.c.product_id} not found.")

            preferences.append(
                GettingProfilePreference(
                    product_id=row.preference.c.product_id,
                    product_name=existing_product.name,
                    max_value=row.preference.c.max_value,
                    value=row.value
                )
            )
        print("After pref_result rows")
        # Query allergens
        stmt = select(user_allergen).where(user_allergen.c.user_id == user_id)
        allergen_results = await db.execute(stmt)
        print(allergen_results)
        allergens = []

        for row in allergen_results:
            # Fetch the product information using the product_id
            existing_allergen = await get_product_by_id(row.user_allergen.c.allergen_id, db)

            if not existing_allergen:
                print(f"Allergen with id {row.user_allergen.c.allergen_id} not found")
                raise ValueError(f"Allergen with ID {row.user_allergen.c.allergen_id} not found.")

            allergens.append(
                GettingAllergen(
                    id=row.user_allergen.c.allergen_id,
                    name=existing_allergen.name
                )
            )

        # Query text_preference and evaluation
        stmt = select(profile_data.c.text_preference, profile_data.c.evaluation).where(
            profile_data.c.user_id == user_id)
        result = await db.execute(stmt)
        profile_data_result = result.first()
        print(profile_data_result)
        return GettingProfile(
            id=user.id,
            username=user.username,
            phone=user.phone,
            preferences=preferences,
            allergens=allergens,
            text_preference=profile_data_result.text_preference if profile_data_result is not None else None,
            evaluation=profile_data_result.evaluation if profile_data_result is not None else None
        )
    except SQLAlchemyError as e:
        raise e


async def get_preferences(db: AsyncSession) -> List[GettingPreference]:
    try:
        stmt = select(preference)
        result = await db.execute(stmt)
        preferences = [
            GettingPreference(
                product_id=row.preference.c.product_id,
                product_name="Product Name",
                max_value=row.preference.c.max_value
            ) for row in result
        ]
        return preferences
    except SQLAlchemyError as e:
        raise e


async def delete_preference(preference_id: int, db: AsyncSession) -> None:
    try:
        stmt = delete(preference).where(preference.c.id == preference_id)
        await db.execute(stmt)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise e
