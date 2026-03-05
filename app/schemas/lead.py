from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    source: str = "website"
    status: str = "new"
    notes: str | None = None
    estimated_value: float | None = None
    assigned_to: UUID | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    source: str | None = None
    status: str | None = None
    notes: str | None = None
    estimated_value: float | None = None
    assigned_to: UUID | None = None


class LeadStatusUpdate(BaseModel):
    status: str


class LeadResponse(LeadBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
