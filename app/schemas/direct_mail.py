from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MailTemplateCreate(BaseModel):
    name: str
    mail_type: str = "postcard"
    size: str = "6x4"
    front_html: str
    back_html: str | None = None
    category: str | None = None
    description: str | None = None


class MailTemplateUpdate(BaseModel):
    name: str | None = None
    mail_type: str | None = None
    size: str | None = None
    front_html: str | None = None
    back_html: str | None = None
    category: str | None = None
    description: str | None = None


class MailTemplateResponse(BaseModel):
    id: UUID
    name: str
    mail_type: str
    size: str
    front_html: str
    back_html: str | None = None
    category: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DirectMailCampaignCreate(BaseModel):
    name: str
    template_id: str | None = None
    mail_type: str = "postcard"
    cost_per_piece: float | None = None
    print_vendor: str | None = None
    notes: str | None = None


class DirectMailCampaignUpdate(BaseModel):
    name: str | None = None
    template_id: str | None = None
    status: str | None = None
    cost_per_piece: float | None = None
    print_vendor: str | None = None
    tracking_number: str | None = None
    notes: str | None = None


class DirectMailCampaignResponse(BaseModel):
    id: UUID
    name: str
    template_id: UUID | None = None
    mail_type: str
    status: str
    recipient_count: int
    estimated_cost: float | None = None
    cost_per_piece: float | None = None
    print_vendor: str | None = None
    tracking_number: str | None = None
    notes: str | None = None
    sent_to_printer_at: datetime | None = None
    mailed_at: datetime | None = None
    delivered_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AddMailRecipientsRequest(BaseModel):
    city: str | None = None
    work_type: str | None = None
    min_score: int | None = None
    max_score: int | None = None
    min_property_value: float | None = None
    max_property_value: float | None = None
    limit: int | None = None


class AddMailRecipientsResponse(BaseModel):
    added: int
    campaign_id: str
