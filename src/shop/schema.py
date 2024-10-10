from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Double


class CreatingShop(BaseModel):
    name: str = Field(..., min_length=1, description="Title must not be empty.")


class GettingShop(CreatingShop):
    id: int
