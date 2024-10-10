from typing import List

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.event.model import event, criterion_event, benefit_event
from src.event.schema import CreatingEvent, GettingEvent
from src.event.criterion.service import create_criterion, delete_criterion
from src.event.benefit.service import create_benefit, delete_benefit


async def create_event(event_data: CreatingEvent, db: AsyncSession) -> GettingEvent:
    try:
        stmt = insert(event).values(
            title=event_data.title,
            description=event_data.description,
            is_active=True  # Новое событие по умолчанию активное
        ).returning(event.c.id, event.c.title, event.c.description, event.c.is_active)

        result = await db.execute(stmt)
        await db.commit()

        event_row = result.fetchone()

        if not event_row:
            raise ValueError("Failed to create event")

        event_id = event_row.id

        # Создаем критерии и связываем их с событием
        if event_data.criteria:
            for criterion_data in event_data.criteria:
                # Используем ранее созданную функцию для создания критерия
                created_criterion = await create_criterion(criterion_data, db)

                # Связываем критерий с событием
                stmt = insert(criterion_event).values(
                    event_id=event_id,
                    criterion_id=created_criterion.id
                )
                await db.execute(stmt)

        # Создаем бенефиты и связываем их с событием
        if event_data.benefits:
            for benefit_data in event_data.benefits:
                # Используем ранее созданную функцию для создания бенефита
                created_benefit = await create_benefit(benefit_data, db)

                # Связываем бенефит с событием
                stmt = insert(benefit_event).values(
                    event_id=event_id,
                    benefit_id=created_benefit.id
                )
                await db.execute(stmt)

        # Финализируем транзакции
        await db.commit()

        return GettingEvent(
            id=event_id,
            title=event_row.title,
            description=event_row.description,
            is_active=event_row.is_active,
            criteria=event_data.criteria or [],
            benefits=event_data.benefits or []
        )

    except IntegrityError as e:
        await db.rollback()
        print(f"Integrity error while creating event: {e}")
        raise e
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Database error while creating event: {e}")
        raise e


# Функция для удаления события
async def delete_event(event_id: int, db: AsyncSession) -> None:
    try:
        # Получаем все критерии, связанные с событием
        criterion_stmt = select(criterion_event.c.criterion_id).where(criterion_event.c.event_id == event_id)
        criterion_results = await db.execute(criterion_stmt)
        criterion_ids = [row.criterion_id for row in criterion_results]

        # Удаляем критерии, используя функцию delete_criterion
        for criterion_id in criterion_ids:
            await delete_criterion(criterion_id, db)

        # Получаем все бенефиты, связанные с событием
        benefit_stmt = select(benefit_event.c.benefit_id).where(benefit_event.c.event_id == event_id)
        benefit_results = await db.execute(benefit_stmt)
        benefit_ids = [row.benefit_id for row in benefit_results]

        # Удаляем бенефиты, используя функцию delete_benefit
        for benefit_id in benefit_ids:
            await delete_benefit(benefit_id, db)

        # Удаляем само событие
        stmt = delete(event).where(event.c.id == event_id)
        result = await db.execute(stmt)

        if result.rowcount == 0:
            raise ValueError(f"Event with id {event_id} not found")

        await db.commit()

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Database error while deleting event: {e}")
        raise e


async def get_active_events(db: AsyncSession) -> List[GettingEvent]:
    try:
        # SQL запрос для получения всех активных событий
        stmt = select(event).where(event.c.is_active == True)
        result = await db.execute(stmt)

        events = result.fetchall()

        # Преобразуем результат в список объектов GettingEvent
        active_events = [
            GettingEvent(
                id=row.id,
                title=row.title,
                description=row.description,
                is_active=row.is_active
            )
            for row in events
        ]

        return active_events

    except SQLAlchemyError as e:
        print(f"Database error while fetching active events: {e}")
        raise e


async def get_all_events(db: AsyncSession) -> List[GettingEvent]:
    try:
        # SQL запрос для получения всех событий
        stmt = select(event)
        result = await db.execute(stmt)

        events = result.fetchall()

        # Преобразуем результат в список объектов GettingEvent
        all_events = [
            GettingEvent(
                id=row.id,
                title=row.title,
                description=row.description,
                is_active=row.is_active
            )
            for row in events
        ]

        return all_events

    except SQLAlchemyError as e:
        print(f"Database error while fetching all events: {e}")
        raise e