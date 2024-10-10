from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Double


class AddingIngredient(BaseModel):
    product_id: int
    value: float = Field(..., gt=0, description="The value must be greater than zero")


class ItemFields(BaseModel):
    title: str = Field(..., min_length=1, description="Title must not be empty.")
    description: Optional[str] = None
    ingredients: List[AddingIngredient]


class GettingIngredients(AddingIngredient):
    name: str
    value_type: str
    cost: float


class GettingItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    ingredients: List[GettingIngredients]
    cost: float


class GettingIngredientValueForItem(BaseModel):
    item_id: int
    value: float
