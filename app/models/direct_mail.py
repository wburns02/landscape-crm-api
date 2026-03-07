import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MailTemplate(Base):
    __tablename__ = "mail_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    mail_type: Mapped[str] = mapped_column(String(50), nullable=False, default="postcard")  # postcard, letter
    size: Mapped[str] = mapped_column(String(50), nullable=False, default="6x4")  # 6x4, 6x9, 8.5x11
    front_html: Mapped[str] = mapped_column(Text, nullable=False)
    back_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    campaigns = relationship("DirectMailCampaign", back_populates="template")


class DirectMailCampaign(Base):
    __tablename__ = "direct_mail_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("mail_templates.id"), nullable=True)
    mail_type: Mapped[str] = mapped_column(String(50), nullable=False, default="postcard")  # postcard, letter
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    # draft -> ready -> sent_to_printer -> printed -> mailed -> delivered
    recipient_count: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_per_piece: Mapped[float | None] = mapped_column(Float, nullable=True)
    print_vendor: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tracking_number: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_to_printer_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mailed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    template = relationship("MailTemplate", back_populates="campaigns")
    recipients = relationship("DirectMailRecipient", back_populates="campaign")


class DirectMailRecipient(Base):
    __tablename__ = "direct_mail_recipients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("direct_mail_campaigns.id"), nullable=False)
    prospect_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prospects.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(10), nullable=False, default="TX")
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    # pending, included, excluded, returned

    campaign = relationship("DirectMailCampaign", back_populates="recipients")
    prospect = relationship("Prospect")
