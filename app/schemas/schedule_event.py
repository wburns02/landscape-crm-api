from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ScheduleEventBase(BaseModel):
    job_id: UUID | None = None
    crew_id: UUID | None = None
    title: str
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    event_type: str = "job"
    color: str | None = None
    notes: str | None = None


class ScheduleEventCreate(ScheduleEventBase):
    pass


class ScheduleEventUpdate(BaseModel):
    job_id: UUID | None = None
    crew_id: UUID | None = None
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    all_day: bool | None = None
    event_type: str | None = None
    color: str | None = None
    notes: str | None = None


class ScheduleEventResponse(ScheduleEventBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
