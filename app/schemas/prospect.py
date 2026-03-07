from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProspectBase(BaseModel):
    first_name: str
    last_name: str
    full_name: str | None = None
    phone: str
    phone_2: str | None = None
    email: str | None = None
    address: str
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    property_value: float | None = None
    sqft: int | None = None
    year_built: int | None = None
    work_type: str | None = None
    lead_score: int | None = None
    source: str | None = None
    import_batch: str | None = None
    status: str = "new"
    email_status: str = "unknown"
    notes: str | None = None


class ProspectCreate(ProspectBase):
    pass


class ProspectUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    phone_2: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    property_value: float | None = None
    sqft: int | None = None
    year_built: int | None = None
    work_type: str | None = None
    lead_score: int | None = None
    status: str | None = None
    email_status: str | None = None
    notes: str | None = None


class ProspectResponse(ProspectBase):
    id: UUID
    last_contacted_at: datetime | None = None
    last_emailed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProspectListResponse(BaseModel):
    items: list[ProspectResponse]
    total: int
    page: int
    page_size: int


class ImportResult(BaseModel):
    imported: int
    skipped: int
    errors: int
    total_processed: int
    batch_id: str
