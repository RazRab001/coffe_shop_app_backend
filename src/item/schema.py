from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Double

from src.product.schema import IngredientValueType


class AddingIngredient(BaseModel):
    product_id: Optional[int] = None
    value: float = Field(..., gt=0, description="The value must be greater than zero")
    name: Optional[str] = None
    value_type: Optional[IngredientValueType] = None


class ItemFields(BaseModel):
    title: str = Field(..., min_length=1, description="Title must not be empty.")
    description: Optional[str] = None
    ingredients: List[AddingIngredient]
    cost: Optional[float] = None
    actualise_cost: Optional[bool] = False


class GettingIngredients(BaseModel):
    name: str
    value_type: str
    product_id: Optional[int] = None
    value: float
    cost: float


class GettingItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    ingredients: List[GettingIngredients]
    cost: float
    actualise_cost: bool
    is_active: bool


class GettingIngredientValueForItem(BaseModel):
    item_id: int
    value: float
