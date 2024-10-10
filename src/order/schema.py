from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Double, Date

from src.item.schema import GettingItem


class OrderItemIngredient(BaseModel):
    product_id: int
    value: float = Field(..., ge=0)


class OrderItem(BaseModel):
    item_id: int
    count: int
    ingredients: List[OrderItemIngredient]


class CreatingOrder(BaseModel):
    #cost: float = Field(..., gt=0)
    date: Date = Field(..., gt=0)
    comment: Optional[str]
    items: List[OrderItem]


class GettingOrder(BaseModel):
    id: int
    user_id: int
    date: Date
    cost: float
    items: List[GettingItem]
