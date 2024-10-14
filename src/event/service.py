from typing import List

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.card.schema import GettingCard
from src.event.benefit.schema import GettingBenefit
from src.event.criterion.schema import GettingCriterion
from src.event.benefit.model import benefit
from src.event.criterion.model import criterion
from src.event.model import event, criterion_event, benefit_event
from src.event.schema import CreatingEvent, GettingEvent, UseAkcesForm
from src.event.criterion.service import create_criterion, delete_criterion
from src.event.benefit.service import create_benefit, delete_benefit
from src.event.utis import benefit_operations, contrast_operations
from src.order.schema import GettingOrder
from src.card.service import get_card_by_id, update_card_count
from src.order.service import get_order_by_id, update_order_total_price


async def create_event(event_data: CreatingEvent, db: AsyncSession) -> GettingEvent:
    try:
        # Вставляем событие без явного создания транзакции
        stmt = insert(event).values(
            title=event_data.title,
            description=event_data.description,
            is_active=True
        ).returning(event.c.id, event.c.title, event.c.description, event.c.is_active)

        result = await db.execute(stmt)
        event_row = result.fetchone()

        if not event_row:
            raise ValueError("Failed to create event")

        event_id = event_row.id

        # Создание критериев
        if event_data.criteria:
            for criterion_data in event_data.criteria:
                created_criterion = await create_criterion(criterion_data, db)

                stmt = insert(criterion_event).values(
                    event_id=event_id,
                    criterion_id=created_criterion.id
                )
                await db.execute(stmt)

        # Создание бенефитов
        if event_data.benefits:
            for benefit_data in event_data.benefits:
                created_benefit = await create_benefit(benefit_data, db)

                stmt = insert(benefit_event).values(
                    event_id=event_id,
                    benefit_id=created_benefit.id
                )
                await db.execute(stmt)

        # Коммитим изменения в конце, если все прошло успешно
        await db.commit()

        # Возвращаем результат
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


async def get_event_by_id(event_id: int, db: AsyncSession) -> GettingEvent:
    try:
        # Fetch event details
        stmt = select(event).where(event.c.id == event_id)
        result = await db.execute(stmt)
        row = result.fetchone()

        if row is None:
            raise ValueError(f"Event with ID {event_id} not found.")

        # Fetch related criteria for the event
        criteria_stmt = select(criterion).join(criterion_event).where(criterion_event.c.event_id == event_id)
        criteria_result = await db.execute(criteria_stmt)
        criteria = [
            GettingCriterion(
                id=criterion_row.id,
                contrast=criterion_row.contrast,
                value=criterion_row.contrast_value
            )
            for criterion_row in criteria_result.fetchall()
        ]

        # Fetch related benefits for the event
        benefits_stmt = select(benefit).join(benefit_event).where(benefit_event.c.event_id == event_id)
        benefits_result = await db.execute(benefits_stmt)
        benefits = [
            GettingBenefit(
                id=benefit_row.id,
                action=benefit_row.action,
                value=benefit_row.action_value
            )
            for benefit_row in benefits_result.fetchall()
        ]

        # Return the event with its criteria and benefits
        get_event = GettingEvent(
            id=row.id,
            title=row.title,
            description=row.description,
            is_active=row.is_active,
            criteria=criteria,
            benefits=benefits
        )

        return get_event

    except SQLAlchemyError as e:
        print(f"Database error while fetching event with ID {event_id}: {e}")
        raise e


async def use_akce(data: UseAkcesForm, db: AsyncSession) -> GettingOrder:
    try:
        print(f"Attempting to use 'akce' for card ID: {data.card_id} and order ID: {data.order_id}")

        # Step 1: Get the bonus card by its ID
        card: GettingCard = await get_card_by_id(data.card_id, db)
        if not card:
            raise ValueError("Can't use akce without bonus card")
        print(f"Found card with ID {card.id}. Current card count: {card.count}, used points: {card.used_points}")

        # Step 2: Get the order by its ID
        order: GettingOrder = await get_order_by_id(data.order_id, db)
        if not order:
            raise ValueError("Can't use akce without order")
        print(f"Found order with ID {order.id}. Total order cost: {order.cost}")

        # Initialize updated values
        updated_card_value = card.count
        used_points = card.used_points
        total_order_cost = order.cost

        # Step 3: Loop through each 'akce' and apply criteria and benefits
        for akce_id in data.akce_ids:
            print(f"Processing 'akce' with ID: {akce_id}")

            # Step 3.1: Get the 'akce' details from the database
            akce: GettingEvent = await get_event_by_id(akce_id, db)
            print(f"Found 'akce' with title: {akce.title}")

            # Step 4: Apply criteria for the 'akce'
            for criterion in akce.criteria:
                comparison_func = contrast_operations.get(criterion.contrast)
                if not comparison_func(order, card, criterion.value):
                    raise ValueError(
                        f"Card or order does not satisfy {criterion.contrast.value} {criterion.value} for akce {akce.title}"
                    )
                print(f"Criterion passed: {criterion.contrast.value} {criterion.value} for 'akce' {akce.title}")

            # Step 5: Apply the benefits for the 'akce'
            for benefit in akce.benefits:
                print(f"Applying benefit with action: {benefit.action} and value: {benefit.value} for 'akce' {akce.title}")

                apply_benefit = benefit_operations.get(benefit.action)
                benefit_result = apply_benefit(order, card, benefit.value)

                # Update the values after applying the benefit
                updated_card_value = benefit_result.card_value
                used_points = benefit_result.used_points
                total_order_cost = benefit_result.total_cost

                print(f"Benefit applied. Updated card value: {updated_card_value}, used points: {used_points}, total order cost: {total_order_cost}")

        # Step 6: Update the card with the new values
        await update_card_count(card.id, updated_card_value, used_points, db)
        print(f"Card updated. New card value: {updated_card_value}, used points: {used_points}")

        # Step 7: Update the order with the new total cost
        await update_order_total_price(order.id, total_order_cost, db)
        print(f"Order updated. New total cost: {total_order_cost}")

        # Step 8: Return the updated order
        updated_order = await get_order_by_id(data.order_id, db)
        print(f"Returning updated order with ID: {updated_order.id}, total cost: {updated_order.cost}")

        return updated_order

    except SQLAlchemyError as e:
        print(f"Database error while using 'akce' effect for card: {e}")
        raise e
