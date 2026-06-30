from __future__ import annotations
from pydantic import BaseModel, field_validator
from typing import Literal
import datetime as dt
from uuid import UUID
from decimal import Decimal


class GoalCreate(BaseModel):
    name: str
    target_amount: Decimal
    deadline: dt.date | None = None

    @field_validator("target_amount")
    @classmethod
    def must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("target_amount must be positive")
        return v


class GoalUpdate(BaseModel):
    name: str | None = None
    target_amount: Decimal | None = None
    deadline: dt.date | None = None
    status: Literal["active", "completed", "cancelled"] | None = None


class ContributionCreate(BaseModel):
    amount: Decimal
    date: dt.date
    note: str | None = None

    @field_validator("amount")
    @classmethod
    def must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v
