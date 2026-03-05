from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TimeEntryBase(BaseModel):
    user_id: UUID
    job_id: UUID | None = None
    clock_in: datetime
    clock_out: datetime | None = None
    hours: float | None = None
    break_minutes: int = 0
    notes: str | None = None
    gps_clock_in: dict | None = None
    gps_clock_out: dict | None = None


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    job_id: UUID | None = None
    clock_in: datetime | None = None
    clock_out: datetime | None = None
    hours: float | None = None
    break_minutes: int | None = None
    notes: str | None = None
    gps_clock_in: dict | None = None
    gps_clock_out: dict | None = None


class ClockInRequest(BaseModel):
    user_id: UUID
    job_id: UUID | None = None
    notes: str | None = None
    gps_clock_in: dict | None = None


class ClockOutRequest(BaseModel):
    user_id: UUID
    break_minutes: int = 0
    notes: str | None = None
    gps_clock_out: dict | None = None


class TimeEntryResponse(TimeEntryBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
