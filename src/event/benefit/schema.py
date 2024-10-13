from pydantic import BaseModel, PositiveFloat

from src.event.benefit.model import Activity


class Benefit(BaseModel):
    action: Activity
    value: PositiveFloat


class GettingBenefit(Benefit):
    id: int
