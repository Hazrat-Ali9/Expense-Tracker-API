from __future__ import annotations

from datetime import date as DateValue
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


TransactionType = Literal["income", "expense"]


class TransactionBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    amount: float = Field(gt=0)
    type: TransactionType
    category: str = Field(min_length=1, max_length=80)
    date: DateValue

    @field_validator("title", "category")
    @classmethod
    def strip_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    amount: float | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)
    date: DateValue | None = None

    @field_validator("title", "category")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "TransactionUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        return self


class TransactionPublic(TransactionBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    message: str
