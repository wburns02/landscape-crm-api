from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PhotoBase(BaseModel):
    job_id: UUID | None = None
    customer_id: UUID | None = None
    url: str
    thumbnail_url: str | None = None
    photo_type: str = "progress"
    caption: str | None = None
    taken_by: UUID | None = None
    taken_at: datetime | None = None


class PhotoCreate(PhotoBase):
    pass


class PhotoUpdate(BaseModel):
    job_id: UUID | None = None
    customer_id: UUID | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    photo_type: str | None = None
    caption: str | None = None
    taken_by: UUID | None = None
    taken_at: datetime | None = None


class PhotoResponse(PhotoBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
