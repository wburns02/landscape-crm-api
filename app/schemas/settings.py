from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class SettingsBase(BaseModel):
    company_name: str = "GreenScape Landscaping"
    company_phone: str | None = None
    company_email: str | None = None
    company_address: str | None = None
    company_logo_url: str | None = None
    tax_rate: float = 8.25
    default_payment_terms_days: int = 30
    business_hours: dict | None = None
    service_area: dict | None = None
    pricing_templates: Any | None = None


class SettingsUpdate(BaseModel):
    company_name: str | None = None
    company_phone: str | None = None
    company_email: str | None = None
    company_address: str | None = None
    company_logo_url: str | None = None
    tax_rate: float | None = None
    default_payment_terms_days: int | None = None
    business_hours: dict | None = None
    service_area: dict | None = None
    pricing_templates: Any | None = None


class SettingsResponse(SettingsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
