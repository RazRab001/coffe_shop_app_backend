from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import insert, select, delete

from src.event.criterion.schema import Criterion, GettingCriterion
from src.event.criterion.model import criterion as criterion_table


# Функция для создания критерия
async def create_criterion(criterion: Criterion, db: AsyncSession) -> GettingCriterion:
    try:
        # Формируем SQL запрос для вставки нового критерия
        stmt = insert(criterion_table).values(
            contrast=criterion.contrast.name,
            contrast_value=criterion.value
        ).returning(criterion_table.c.id, criterion_table.c.contrast, criterion_table.c.contrast_value)

        # Выполняем запрос
        result = await db.execute(stmt)
        await db.commit()

        # Получаем данные новой записи
        criterion_row = result.fetchone()
        if criterion_row:
            return GettingCriterion(
                id=criterion_row.id,
                contrast=criterion_row.contrast,
                value=criterion_row.contrast_value
            )
    except IntegrityError as e:
        await db.rollback()  # Откат транзакции в случае ошибки
        print(f"Integrity error while creating criterion: {e}")
        raise e
    except SQLAlchemyError as e:
        await db.rollback()  # Откат транзакции в случае ошибки
        print(f"Database error while creating criterion: {e}")
        raise e


# Функция для удаления критерия
async def delete_criterion(criterion_id: int, db: AsyncSession) -> None:
    try:
        # Формируем SQL запрос для удаления критерия по id
        stmt = delete(criterion_table).where(criterion_table.c.id == criterion_id)

        # Выполняем запрос
        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:
            raise ValueError(f"Criterion with id {criterion_id} not found")

    except SQLAlchemyError as e:
        await db.rollback()  # Откат транзакции в случае ошибки
        print(f"Database error while deleting criterion: {e}")
        raise e
