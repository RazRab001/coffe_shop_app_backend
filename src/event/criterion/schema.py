from pydantic import BaseModel, PositiveFloat

from src.event.criterion.model import Contrast


class Criterion(BaseModel):
    contrast: Contrast
    value: PositiveFloat


class GettingCriterion(Criterion):
    id: int
