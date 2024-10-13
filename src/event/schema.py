from typing import Optional, List

from pydantic import BaseModel

from src.event.criterion.schema import Criterion
from src.event.benefit.schema import Benefit


class CreatingEvent(BaseModel):
    title: str
    description: Optional[str] = None
    criteria: Optional[List[Criterion]] = []
    benefits: Optional[List[Benefit]] = []


class GettingEvent(CreatingEvent):
    id: int
    is_active: bool


class UseAkcesForm(BaseModel):
    card_id: int
    order_id: int
    akce_ids: List[int]
