from pydantic import BaseModel, PositiveFloat

from src.event.benefit.model import Action


class Benefit(BaseModel):
    action: Action
    value: PositiveFloat
