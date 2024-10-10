from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import insert, delete, select
from pydantic import PositiveFloat
from typing import Optional
from src.event.benefit.model import benefit as benefit_table
from src.event.benefit.schema import Benefit


async def create_benefit(benefit_data: Benefit, db: AsyncSession) -> Optional[Benefit]:
    try:
        # Создаем SQL запрос на вставку данных в таблицу benefit
        stmt = insert(benefit_table).values(
            action=benefit_data.action,
            action_value=benefit_data.value
        ).returning(benefit_table.c.id, benefit_table.c.action, benefit_table.c.action_value)

        # Выполняем запрос и коммитим изменения
        result = await db.execute(stmt)
        await db.commit()

        # Получаем данные новой записи
        benefit_row = result.fetchone()
        if benefit_row:
            return Benefit(
                action=benefit_row.action,
                value=benefit_row.action_value
            )

    except IntegrityError as e:
        await db.rollback()  # Откат транзакции в случае ошибки
        print(f"Integrity error while creating benefit: {e}")
        raise e
    except SQLAlchemyError as e:
        await db.rollback()  # Откат транзакции в случае ошибки
        print(f"Database error while creating benefit: {e}")
        raise e


# Функция для удаления записи из таблицы benefit по id
async def delete_benefit(benefit_id: int, db: AsyncSession) -> None:
    try:
        # Формируем SQL запрос на удаление записи по id
        stmt = delete(benefit_table).where(benefit_table.c.id == benefit_id)

        # Выполняем запрос и коммитим изменения
        result = await db.execute(stmt)
        await db.commit()

        # Если строка не была удалена, поднимаем исключение
        if result.rowcount == 0:
            raise ValueError(f"Benefit with id {benefit_id} not found")

    except SQLAlchemyError as e:
        await db.rollback()  # Откат транзакции в случае ошибки
        print(f"Database error while deleting benefit: {e}")
        raise e
