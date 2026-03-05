from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobBase(BaseModel):
    customer_id: UUID
    title: str
    description: str | None = None
    job_type: str = "maintenance"
    status: str = "pending"
    priority: str = "normal"
    scheduled_date: str | None = None
    scheduled_time: str | None = None
    estimated_duration_hours: float | None = None
    actual_duration_hours: float | None = None
    crew_id: UUID | None = None
    notes: str | None = None
    materials_used: list | None = None
    before_photos: list | None = None
    after_photos: list | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    is_recurring: bool = False
    recurrence_rule: str | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    customer_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    job_type: str | None = None
    status: str | None = None
    priority: str | None = None
    scheduled_date: str | None = None
    scheduled_time: str | None = None
    estimated_duration_hours: float | None = None
    actual_duration_hours: float | None = None
    crew_id: UUID | None = None
    notes: str | None = None
    materials_used: list | None = None
    before_photos: list | None = None
    after_photos: list | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    is_recurring: bool | None = None
    recurrence_rule: str | None = None


class JobStatusUpdate(BaseModel):
    status: str


class JobResponse(JobBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
