from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    company_name: str | None = None
    customer_type: str = "residential"
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    lat: float | None = None
    lng: float | None = None
    property_size_sqft: int | None = None
    notes: str | None = None
    tags: list | None = None
    source: str | None = None
    site_photos: list | None = None
    site_map_url: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None
    customer_type: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    lat: float | None = None
    lng: float | None = None
    property_size_sqft: int | None = None
    notes: str | None = None
    tags: list | None = None
    source: str | None = None
    total_spent: float | None = None
    job_count: int | None = None
    site_photos: list | None = None
    site_map_url: str | None = None


class CustomerResponse(CustomerBase):
    id: UUID
    total_spent: float
    job_count: int
    created_at: datetime
    updated_at: datetime
    # Frontend-compatible aliases
    name: str = ""
    type: str = ""
    zip: str | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def populate_aliases(self) -> "CustomerResponse":
        if not self.name:
            self.name = self.company_name or f"{self.first_name} {self.last_name}".strip()
        if not self.type:
            self.type = self.customer_type
        if self.zip is None:
            self.zip = self.zip_code
        return self
