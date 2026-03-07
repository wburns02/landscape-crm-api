from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# --- Templates ---

class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    html_body: str
    text_body: str | None = None
    category: str | None = None


class EmailTemplateCreate(EmailTemplateBase):
    pass


class EmailTemplateUpdate(BaseModel):
    name: str | None = None
    subject: str | None = None
    html_body: str | None = None
    text_body: str | None = None
    category: str | None = None


class EmailTemplateResponse(EmailTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Campaigns ---

class EmailCampaignCreate(BaseModel):
    name: str
    template_id: UUID | None = None
    send_at: datetime | None = None


class EmailCampaignUpdate(BaseModel):
    name: str | None = None
    template_id: UUID | None = None
    send_at: datetime | None = None


class EmailCampaignResponse(BaseModel):
    id: UUID
    name: str
    template_id: UUID | None = None
    status: str
    send_at: datetime | None = None
    sent_count: int
    open_count: int
    click_count: int
    bounce_count: int
    recipient_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CampaignStatsResponse(BaseModel):
    id: UUID
    name: str
    status: str
    total_recipients: int
    sent: int
    opened: int
    clicked: int
    bounced: int
    open_rate: float
    click_rate: float
    bounce_rate: float


# --- Recipients ---

class AddProspectsRequest(BaseModel):
    city: str | None = None
    work_type: str | None = None
    min_score: int | None = None
    max_score: int | None = None
    min_property_value: float | None = None
    max_property_value: float | None = None
    limit: int | None = None


class AddProspectsResponse(BaseModel):
    added: int
    campaign_id: UUID


# --- Send ---

class SendTestRequest(BaseModel):
    to_email: str
    template_id: UUID | None = None
    subject: str | None = None
    html_body: str | None = None


class SendTestResponse(BaseModel):
    success: bool
    message: str
    resend_id: str | None = None


# --- AI Recommendations ---

class SegmentRecommendation(BaseModel):
    segment_name: str
    description: str
    prospect_count: int
    avg_lead_score: float
    avg_property_value: float
    suggested_template: str


class AIRecommendationResponse(BaseModel):
    segments: list[SegmentRecommendation]
    best_send_times: list[str]
    cadence: list[str]
    total_unreached: int
