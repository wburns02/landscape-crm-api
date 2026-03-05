from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EquipmentBase(BaseModel):
    name: str
    equipment_type: str = "mower"
    make: str | None = None
    model: str | None = None
    serial_number: str | None = None
    year: int | None = None
    status: str = "available"
    purchase_date: str | None = None
    purchase_price: float | None = None
    current_value: float | None = None
    last_maintenance_date: str | None = None
    next_maintenance_date: str | None = None
    assigned_crew_id: UUID | None = None
    fuel_type: str | None = None
    hours_used: float = 0
    notes: str | None = None
    image_url: str | None = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: str | None = None
    equipment_type: str | None = None
    make: str | None = None
    model: str | None = None
    serial_number: str | None = None
    year: int | None = None
    status: str | None = None
    purchase_date: str | None = None
    purchase_price: float | None = None
    current_value: float | None = None
    last_maintenance_date: str | None = None
    next_maintenance_date: str | None = None
    assigned_crew_id: UUID | None = None
    fuel_type: str | None = None
    hours_used: float | None = None
    notes: str | None = None
    image_url: str | None = None


class EquipmentStatusUpdate(BaseModel):
    status: str


class EquipmentResponse(EquipmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
