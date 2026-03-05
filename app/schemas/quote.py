from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QuoteBase(BaseModel):
    customer_id: UUID
    title: str
    status: str = "draft"
    line_items: list | None = None
    subtotal: float = 0
    tax_rate: float = 8.25
    tax_amount: float = 0
    total: float = 0
    notes: str | None = None
    valid_until: str | None = None


class QuoteCreate(QuoteBase):
    quote_number: str | None = None


class QuoteUpdate(BaseModel):
    customer_id: UUID | None = None
    title: str | None = None
    status: str | None = None
    line_items: list | None = None
    subtotal: float | None = None
    tax_rate: float | None = None
    tax_amount: float | None = None
    total: float | None = None
    notes: str | None = None
    valid_until: str | None = None


class QuoteResponse(QuoteBase):
    id: UUID
    quote_number: str
    sent_at: datetime | None
    accepted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
