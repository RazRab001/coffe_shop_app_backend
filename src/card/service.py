from typing import Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, delete, update, select

from src.auth.models import User
from src.card.model import bonus_card
from src.card.schema import CreatingCard, UpdatingCard, GettingCard


async def create_card(card_data: CreatingCard, db: AsyncSession) -> Optional[GettingCard]:
    """
    Создание новой бонусной карты
    """
    try:
        # Проверка, существует ли уже карта с таким номером телефона
        existing_card = await db.execute(select(bonus_card).where(bonus_card.c.phone == card_data.phone_number))
        if existing_card.scalar():
            return None  # Карта с таким номером уже существует

        # Вставка новой карты
        stmt = insert(bonus_card).values(
            phone=card_data.phone_number,
            user_id=card_data.user_id,
            count=0
        ).returning(bonus_card.c.id, bonus_card.c.phone, bonus_card.c.user_id, bonus_card.c.count, bonus_card.c.used_points)

        result = await db.execute(stmt)
        await db.commit()

        card_row = result.fetchone()

        if card_row:
            return GettingCard(
                id=card_row.id,
                phone=card_row.phone,
                user_id=card_row.user_id,
                count=card_row.count,
                used_points=card_row.used_points
            )

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error creating bonus card: {e}")
        raise e


async def update_card(id: int, card_update: UpdatingCard, db: AsyncSession) -> Optional[GettingCard]:
    """
    Обновление данных карты (номер телефона или бонусы)
    """
    try:
        # Поиск существующей карты по ID
        card = await get_card_by_id(id, db)

        if not card:
            return None  # Карта не найдена

        # Собираем данные для обновления, исключаем unset поля
        card_update_data = card_update.dict(exclude_unset=True)

        # Обработка бонусов
        if "adding_bonus" in card_update_data:
            # Если добавляются положительные бонусы — увеличиваем count
            if card_update.adding_bonus > 0:
                card.count += card_update.adding_bonus
            # Если отрицательные бонусы — уменьшаем count и увеличиваем used_points
            elif card_update.adding_bonus < 0:
                abs_bonus = abs(card_update.adding_bonus)
                if card.count >= abs_bonus:
                    card.count -= abs_bonus
                    card.used_points += abs_bonus
                else:
                    raise ValueError("Not enough bonus points to deduct")

            # Удаляем 'adding_bonus', так как это не поле в базе данных
            card_update_data.pop("adding_bonus")

        # Обновление номера телефона, если он был передан
        if "phone_number" in card_update_data:
            card.phone = card_update.phone_number

        # Обновление поля 'user_id', если нужно
        if "user_id" in card_update_data:
            card.user_id = card_update.user_id

        # Формируем SQL запрос на обновление
        stmt = (
            update(bonus_card)
            .where(bonus_card.c.id == id)
            .values(
                phone=card.phone,
                count=card.count,
                used_points=card.used_points,
                user_id=card.user_id,
            )
            .returning(
                bonus_card.c.id,
                bonus_card.c.user_id,
                bonus_card.c.phone,
                bonus_card.c.count,
                bonus_card.c.used_points,
            )
        )

        # Выполняем запрос и коммитим изменения
        result = await db.execute(stmt)
        await db.commit()

        updated_card_row = result.fetchone()

        if updated_card_row:
            return GettingCard(
                id=updated_card_row.id,
                phone=updated_card_row.phone,
                user_id=updated_card_row.user_id,
                count=updated_card_row.count,
                used_points=updated_card_row.used_points,
            )

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error updating bonus card: {e}")
        raise e


async def get_card_by_phone(phone_number: str, db: AsyncSession) -> Optional[GettingCard]:
    """
    Получение информации о бонусной карте по номеру телефона
    """
    try:
        stmt = select(bonus_card).where(bonus_card.c.phone == phone_number)
        result = await db.execute(stmt)
        card_row = result.fetchone()

        if card_row:
            return GettingCard(
                id=card_row.id,
                phone=card_row.phone,
                user_id=card_row.user_id,
                count=card_row.count,
                used_points=card_row.used_points
            )

        return None

    except SQLAlchemyError as e:
        print(f"Error retrieving bonus card: {e}")
        raise e


async def get_card_by_id(card_id: int, db: AsyncSession) -> Optional[GettingCard]:
    """
    Получение информации о бонусной карте по ID
    """
    try:
        stmt = select(bonus_card).where(bonus_card.c.id == card_id)
        result = await db.execute(stmt)
        card_row = result.fetchone()

        if card_row:
            return GettingCard(
                id=card_row.id,
                phone=card_row.phone,
                user_id=card_row.user_id,
                count=card_row.count,
                used_points=card_row.used_points
            )
        return None

    except SQLAlchemyError as e:
        print(f"Error retrieving bonus card by ID: {e}")
        raise e


async def get_card_by_user(user_id: UUID, db: AsyncSession) -> Optional[GettingCard]:
    """
    Сначала пытается найти бонусную карту по user_id.
    Если карта не найдена, ищет пользователя по user_id, затем ищет карту по его номеру телефона.
    """
    try:
        # 1. Попытка найти карту по user_id
        card_stmt = select(bonus_card).where(bonus_card.c.user_id == user_id)
        result = await db.execute(card_stmt)
        card_row = result.fetchone()

        if card_row:
            # Если карта найдена, возвращаем её
            return GettingCard(
                id=card_row.id,
                phone=card_row.phone,
                user_id=card_row.user_id,
                count=card_row.count,
                used_points=card_row.used_points
            )

        # 2. Если карта не найдена, ищем пользователя по user_id
        user_stmt = select(User).where(User.id == user_id)
        result = await db.execute(user_stmt)
        user_row = result.fetchone()

        if not user_row:
            return None  # Если пользователь не найден, возвращаем None

        # 3. Ищем карту по номеру телефона пользователя
        card_by_phone = await get_card_by_phone(user_row.phone, db)
        return card_by_phone  # Если карта найдена по телефону, она будет возвращена

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error occurred while fetching card by user: {e}")
        raise e


async def delete_card(id: int, db: AsyncSession) -> bool:
    """
    Удаление бонусной карты по номеру телефона
    """
    try:
        stmt = delete(bonus_card).where(bonus_card.c.id == id)
        result = await db.execute(stmt)
        await db.commit()

        return result.rowcount > 0  # Возвращаем True, если карта была удалена

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error deleting bonus card: {e}")
        raise e


async def update_card_count(card_id: int, new_count: int, new_used_points: int, db: AsyncSession) -> None:
    try:
        stmt = (
            update(bonus_card)
            .where(bonus_card.c.id == card_id)
            .values(count=new_count, used_points=new_used_points)
        )
        await db.execute(stmt)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Database error while updating card count: {e}")
        raise e
