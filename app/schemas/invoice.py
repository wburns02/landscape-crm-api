from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InvoiceBase(BaseModel):
    customer_id: UUID
    job_id: UUID | None = None
    quote_id: UUID | None = None
    status: str = "draft"
    line_items: list | None = None
    subtotal: float = 0
    tax_rate: float = 8.25
    tax_amount: float = 0
    total: float = 0
    paid_amount: float = 0
    due_date: str | None = None
    notes: str | None = None


class InvoiceCreate(InvoiceBase):
    invoice_number: str | None = None


class InvoiceUpdate(BaseModel):
    customer_id: UUID | None = None
    job_id: UUID | None = None
    quote_id: UUID | None = None
    status: str | None = None
    line_items: list | None = None
    subtotal: float | None = None
    tax_rate: float | None = None
    tax_amount: float | None = None
    total: float | None = None
    paid_amount: float | None = None
    due_date: str | None = None
    notes: str | None = None


class RecordPaymentRequest(BaseModel):
    amount: float
    method: str = "card"
    reference_number: str | None = None
    notes: str | None = None


class InvoiceResponse(InvoiceBase):
    id: UUID
    invoice_number: str
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
