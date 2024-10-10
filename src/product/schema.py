from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Double


class IngredientValueType(str, Enum):
    KILOGRAM = "kilogram"
    UNIT = "unit"
    LITER = "liter"


class CreationProduct(BaseModel):
    title: str = Field(..., min_length=1, description="Title must not be empty.")
    value_type: IngredientValueType
    allergens: Optional[List[int]]


class AddingProduct(BaseModel):
    value: float = Field(..., gt=0, description="The value must be greater than zero")
    unit_cost: float = Field(..., gt=0, description="The value must be greater than zero")
    shop_id: int


class GettingProduct(BaseModel):
    id: int
    name: str
    value: float
    value_type: str
    unit_cost: float
    allergens: Optional[List[str]]


class ReducingProduct(BaseModel):
    value: float = Field(..., gt=0, description="The value must be greater than zero")
