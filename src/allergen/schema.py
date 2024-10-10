from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Double


class CreatingAllergen(BaseModel):
    name: str


class GettingAllergen(CreatingAllergen):
    id: int
