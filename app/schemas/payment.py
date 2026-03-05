from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PaymentBase(BaseModel):
    invoice_id: UUID
    amount: float
    method: str = "card"
    reference_number: str | None = None
    notes: str | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: float | None = None
    method: str | None = None
    reference_number: str | None = None
    notes: str | None = None


class PaymentResponse(PaymentBase):
    id: UUID
    paid_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
