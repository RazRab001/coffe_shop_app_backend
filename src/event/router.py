from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.models import User
from src.dependencies import get_db, permission_dependency
from src.event.schema import CreatingEvent, GettingEvent
from src.event.service import create_event, get_all_events, get_active_events, delete_event

router = APIRouter(
    prefix="/akce",
)


@router.post("", response_model=GettingEvent)
async def create_new_akce(event: CreatingEvent,
                          db: AsyncSession = Depends(get_db),
                          user: User = Depends(permission_dependency("create_event"))) -> GettingEvent:
    created_event = await create_event(event, db)
    if not created_event:
        raise HTTPException(status_code=400, detail="Failed to create akce")
    return created_event


@router.get("", response_model=List[GettingEvent])
async def get_active_akce(db: AsyncSession = Depends(get_db)) -> List[GettingEvent]:
    try:
        return await get_active_events(db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.get("/all", response_model=List[GettingEvent])
async def get_all_akce(db: AsyncSession = Depends(get_db),
                       user: User = Depends(permission_dependency("get_events"))) -> List[GettingEvent]:
    try:
        return await get_all_events(db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_akce(event_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(permission_dependency("delete_event"))) -> None:
    await delete_event(event_id, db)
