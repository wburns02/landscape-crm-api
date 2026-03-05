import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, default="GreenScape Landscaping")
    company_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    company_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tax_rate: Mapped[float] = mapped_column(Float, default=8.25)
    default_payment_terms_days: Mapped[int] = mapped_column(Integer, default=30)
    business_hours: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    service_area: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    pricing_templates: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
