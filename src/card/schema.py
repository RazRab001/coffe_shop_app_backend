from uuid import UUID

from pydantic import BaseModel, Field, constr, validator
from typing import Optional, Annotated
import re

from pydantic_extra_types.phone_numbers import PhoneNumber


class CreatingCard(BaseModel):
    phone_number: PhoneNumber
    user_id: Optional[UUID] = None


class UpdatingCard(BaseModel):
    phone_number: Optional[PhoneNumber] = None
    user_id: Optional[UUID] = None
    adding_bonus: Optional[int] = 0


class GettingCard(BaseModel):
    id: int
    phone: str
    user_id: Optional[UUID] = None
    count: int
    used_points: int
