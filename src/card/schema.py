from pydantic import BaseModel, Field, constr, validator
from typing import Optional, Annotated
import re

from pydantic_extra_types.phone_numbers import PhoneNumber


class CreatingCard(BaseModel):
    phone_number: PhoneNumber


class UpdatingCard(BaseModel):
    phone_number: Optional[PhoneNumber] = None
    user_id: Optional[str] = None
    adding_bonus: Optional[int] = Field(0, ge=0)


class GettingCard(BaseModel):
    id: int
    phone: str
    count: int
    used_points: int
