from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, delete, update, select

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
            count=0  # Начальное значение бонусов
        ).returning(bonus_card.c.id, bonus_card.c.phone, bonus_card.c.count)

        result = await db.execute(stmt)
        await db.commit()

        card_row = result.fetchone()

        if card_row:
            return GettingCard(id=card_row.id, phone=card_row.phone, count=card_row.count)

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error creating bonus card: {e}")
        raise e


async def update_card(id: int, card_update: UpdatingCard, db: AsyncSession) -> Optional[GettingCard]:
    """
    Обновление данных карты (номер телефона или бонусы)
    """
    try:
        # Поиск существующей карты по номеру телефона
        result = await db.execute(select(bonus_card).where(bonus_card.c.id == id))
        card = result.scalar()

        if not card:
            return None  # Карта не найдена

        # Собираем данные для обновления
        card_update_data = card_update.dict(exclude_unset=True)

        # Если есть добавление бонусов, увеличиваем счетчик
        if "adding_bonus" in card_update_data:
            card_update_data["count"] = card.count + card_update.adding_bonus

        # Обновляем данные карты
        stmt = update(bonus_card).where(bonus_card.c.id == id).values(**card_update_data).returning(
            bonus_card.c.id, bonus_card.c.phone, bonus_card.c.count)
        result = await db.execute(stmt)
        await db.commit()

        updated_card_row = result.fetchone()

        if updated_card_row:
            return GettingCard(id=updated_card_row.id, phone=updated_card_row.phone, count=updated_card_row.count)

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
            return GettingCard(id=card_row.id, phone=card_row.phone, count=card_row.count)

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
            return GettingCard(id=card_row.id, phone=card_row.phone, count=card_row.count)

        return None

    except SQLAlchemyError as e:
        print(f"Error retrieving bonus card by ID: {e}")
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
