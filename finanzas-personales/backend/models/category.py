from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from uuid import UUID


class CategoryCreate(BaseModel):
    name: str
    icon: str = "📦"
    type: Literal["income", "expense"]
    color: str = "#6366f1"


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    color: str | None = None


class Category(CategoryCreate):
    id: UUID
    created_at: datetime
