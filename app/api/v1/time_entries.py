from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.time_entry import TimeEntry
from app.schemas.time_entry import ClockInRequest, ClockOutRequest, TimeEntryCreate, TimeEntryResponse, TimeEntryUpdate

router = APIRouter(prefix="/time-entries", tags=["time-entries"])


@router.get("", response_model=list[TimeEntryResponse])
async def list_time_entries(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: UUID | None = None,
    job_id: UUID | None = None,
):
    query = select(TimeEntry)
    if user_id:
        query = query.where(TimeEntry.user_id == user_id)
    if job_id:
        query = query.where(TimeEntry.job_id == job_id)
    query = query.order_by(TimeEntry.clock_in.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/by-user/{user_id}", response_model=list[TimeEntryResponse])
async def get_by_user(user_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(TimeEntry).where(TimeEntry.user_id == user_id).order_by(TimeEntry.clock_in.desc())
    )
    return result.scalars().all()


@router.get("/{entry_id}", response_model=TimeEntryResponse)
async def get_time_entry(entry_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(TimeEntry).where(TimeEntry.id == entry_id))
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("TimeEntry", str(entry_id))
    return entry


@router.post("", response_model=TimeEntryResponse, status_code=201)
async def create_time_entry(data: TimeEntryCreate, db: DbSession, current_user: CurrentUser):
    entry = TimeEntry(**data.model_dump())
    if entry.clock_out and entry.clock_in:
        diff = (entry.clock_out - entry.clock_in).total_seconds() / 3600
        entry.hours = round(diff - (entry.break_minutes or 0) / 60, 2)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.post("/clock-in", response_model=TimeEntryResponse, status_code=201)
async def clock_in(data: ClockInRequest, db: DbSession, current_user: CurrentUser):
    # Check if user already has an open entry
    result = await db.execute(
        select(TimeEntry)
        .where(TimeEntry.user_id == data.user_id)
        .where(TimeEntry.clock_out == None)
    )
    existing = result.scalars().first()
    if existing:
        raise ValidationError("User already has an open time entry. Clock out first.")

    entry = TimeEntry(
        user_id=data.user_id,
        job_id=data.job_id,
        clock_in=datetime.now(timezone.utc),
        notes=data.notes,
        gps_clock_in=data.gps_clock_in,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.post("/clock-out", response_model=TimeEntryResponse)
async def clock_out(data: ClockOutRequest, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(TimeEntry)
        .where(TimeEntry.user_id == data.user_id)
        .where(TimeEntry.clock_out == None)
        .order_by(TimeEntry.clock_in.desc())
    )
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("No open time entry found for user")

    entry.clock_out = datetime.now(timezone.utc)
    entry.break_minutes = data.break_minutes
    entry.gps_clock_out = data.gps_clock_out
    if data.notes:
        entry.notes = (entry.notes or "") + "\n" + data.notes if entry.notes else data.notes

    diff = (entry.clock_out - entry.clock_in).total_seconds() / 3600
    entry.hours = round(diff - (entry.break_minutes or 0) / 60, 2)

    await db.commit()
    await db.refresh(entry)
    return entry


@router.patch("/{entry_id}", response_model=TimeEntryResponse)
async def update_time_entry(entry_id: UUID, data: TimeEntryUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(TimeEntry).where(TimeEntry.id == entry_id))
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("TimeEntry", str(entry_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    # Recalculate hours if both in/out present
    if entry.clock_out and entry.clock_in:
        diff = (entry.clock_out - entry.clock_in).total_seconds() / 3600
        entry.hours = round(diff - (entry.break_minutes or 0) / 60, 2)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}")
async def delete_time_entry(entry_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(TimeEntry).where(TimeEntry.id == entry_id))
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("TimeEntry", str(entry_id))
    await db.delete(entry)
    await db.commit()
    return {"message": "Time entry deleted"}
