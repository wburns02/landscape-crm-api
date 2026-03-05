import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, default="maintenance")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    scheduled_date: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    scheduled_time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estimated_duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    crew_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("crews.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    materials_used: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    before_photos: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    after_photos: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="jobs")
    crew = relationship("Crew", back_populates="jobs")
    schedule_events = relationship("ScheduleEvent", back_populates="job")
    invoices = relationship("Invoice", back_populates="job")
    time_entries = relationship("TimeEntry", back_populates="job")
    photos = relationship("Photo", back_populates="job")
