import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    html_body: Mapped[str] = mapped_column(Text, nullable=False)
    text_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    campaigns = relationship("EmailCampaign", back_populates="template")


class EmailCampaign(Base):
    __tablename__ = "email_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("email_templates.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    send_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    open_count: Mapped[int] = mapped_column(Integer, default=0)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    bounce_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    template = relationship("EmailTemplate", back_populates="campaigns")
    recipients = relationship("EmailCampaignRecipient", back_populates="campaign")


class EmailCampaignRecipient(Base):
    __tablename__ = "email_campaign_recipients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_campaigns.id"), nullable=False)
    prospect_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prospects.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign = relationship("EmailCampaign", back_populates="recipients")
    prospect = relationship("Prospect")


class EmailSend(Base):
    __tablename__ = "email_sends"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prospect_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("prospects.id"), nullable=True)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("email_campaigns.id"), nullable=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("email_templates.id"), nullable=True)
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    resend_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    bounced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
