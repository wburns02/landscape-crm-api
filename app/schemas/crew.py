from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CrewBase(BaseModel):
    name: str
    leader_id: UUID | None = None
    color: str | None = "#22c55e"
    is_active: bool = True


class CrewCreate(CrewBase):
    pass


class CrewUpdate(BaseModel):
    name: str | None = None
    leader_id: UUID | None = None
    color: str | None = None
    is_active: bool | None = None


class CrewResponse(CrewBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CrewMemberBase(BaseModel):
    crew_id: UUID
    user_id: UUID
    role: str = "member"


class CrewMemberCreate(BaseModel):
    user_id: UUID
    role: str = "member"


class CrewMemberResponse(CrewMemberBase):
    id: UUID
    joined_at: datetime

    model_config = {"from_attributes": True}
