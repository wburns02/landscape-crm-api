from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ContractBase(BaseModel):
    customer_id: UUID
    title: str
    contract_type: str = "maintenance"
    status: str = "active"
    services: list | None = None
    price_per_visit: float = 0
    total_value: float = 0
    visit_frequency: str = "weekly"
    start_date: str | None = None
    end_date: str | None = None
    auto_renew: bool = False
    notes: str | None = None


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    customer_id: UUID | None = None
    title: str | None = None
    contract_type: str | None = None
    status: str | None = None
    services: list | None = None
    price_per_visit: float | None = None
    total_value: float | None = None
    visit_frequency: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    auto_renew: bool | None = None
    notes: str | None = None


class ContractResponse(ContractBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
