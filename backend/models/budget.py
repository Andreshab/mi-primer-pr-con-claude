from __future__ import annotations
from pydantic import BaseModel, field_validator
from decimal import Decimal


class BudgetUpsert(BaseModel):
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v
