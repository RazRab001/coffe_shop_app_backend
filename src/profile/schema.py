from typing import List
from uuid import UUID

from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber
from src.allergen.schema import GettingAllergen


class CreatingPreference(BaseModel):
    product_id: int
    max_value: int


class GettingPreference(CreatingPreference):
    product_name: str


class CreatingProfilePreference(CreatingPreference):
    value: int


class GettingProfilePreference(GettingPreference):
    value: int


class Allergen(BaseModel):
    allergen_id: int


class UpdatingProfile(BaseModel):
    username: str
    phone: PhoneNumber
    preferences: List[CreatingProfilePreference]
    allergens: List[Allergen]
    text_preference: str


class GettingProfile(BaseModel):
    id: UUID
    username: str
    phone: PhoneNumber
    preferences: List[GettingProfilePreference]
    allergens: List[GettingAllergen]
    text_preference: str
    evaluation: float

