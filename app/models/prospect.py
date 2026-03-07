import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prospect(Base):
    __tablename__ = "prospects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_2: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    property_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    sqft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_built: Mapped[int | None] = mapped_column(Integer, nullable=True)
    work_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    import_batch: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="new", index=True)
    email_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_emailed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_prospects_address_unique", "address", "city", "state", unique=True),
    )
