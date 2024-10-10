from typing import Optional, List

from pydantic import BaseModel

from src.event.criterion.schema import Criterion
from src.event.benefit.schema import Benefit


class CreatingEvent(BaseModel):
    title: str
    description: Optional[str]
    criteria: Optional[List[Criterion]]
    benefits: Optional[List[Benefit]]


class GettingEvent(CreatingEvent):
    id: int
    is_active: bool
