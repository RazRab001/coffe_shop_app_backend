from enum import Enum
from typing import Optional, List
from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Double, Date

from src.item.schema import GettingItem


class OrderItemIngredient(BaseModel):
    product_id: int
    value: float = Field(..., ge=0)


class OrderItem(BaseModel):
    item_id: int
    count: int
    ingredients: Optional[List[OrderItemIngredient]] = []


class CreatingOrder(BaseModel):
    user_id: Optional[UUID] = None
    comment: Optional[str] = None
    items: List[OrderItem]


class GettingOrder(BaseModel):
    id: int
    user_id: Optional[int]
    date: date
    cost: float
    items: List[GettingItem]
