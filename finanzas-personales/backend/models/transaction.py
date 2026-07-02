from pydantic import BaseModel, field_validator
from typing import Literal
import datetime as dt
from uuid import UUID
from decimal import Decimal


class TransactionCreate(BaseModel):
    amount: Decimal
    type: Literal["income", "expense"]
    category_id: UUID
    description: str | None = None
    date: dt.date

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v


class TransactionUpdate(BaseModel):
    amount: Decimal | None = None
    category_id: UUID | None = None
    description: str | None = None
    date: dt.date | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("amount must be positive")
        return v


class Transaction(TransactionCreate):
    id: UUID
    source: Literal["manual", "import"]
    created_at: dt.datetime
