from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError
from app.models.schedule_event import ScheduleEvent
from app.schemas.schedule_event import ScheduleEventCreate, ScheduleEventResponse, ScheduleEventUpdate

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("", response_model=list[ScheduleEventResponse])
async def list_events(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    result = await db.execute(
        select(ScheduleEvent).order_by(ScheduleEvent.start_time.asc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/week", response_model=list[ScheduleEventResponse])
async def get_week_events(
    db: DbSession,
    current_user: CurrentUser,
    date_str: str = Query(alias="date", default=None),
):
    if date_str:
        start = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    else:
        today = date.today()
        start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

    # Go to Monday of this week
    start = start - timedelta(days=start.weekday())
    end = start + timedelta(days=7)

    result = await db.execute(
        select(ScheduleEvent)
        .where(ScheduleEvent.start_time >= start)
        .where(ScheduleEvent.start_time < end)
        .order_by(ScheduleEvent.start_time.asc())
    )
    return result.scalars().all()


@router.get("/crew/{crew_id}", response_model=list[ScheduleEventResponse])
async def get_crew_schedule(
    crew_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    result = await db.execute(
        select(ScheduleEvent)
        .where(ScheduleEvent.crew_id == crew_id)
        .order_by(ScheduleEvent.start_time.asc())
    )
    return result.scalars().all()


@router.get("/{event_id}", response_model=ScheduleEventResponse)
async def get_event(event_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(ScheduleEvent).where(ScheduleEvent.id == event_id))
    event = result.scalars().first()
    if not event:
        raise NotFoundError("ScheduleEvent", str(event_id))
    return event


@router.post("", response_model=ScheduleEventResponse, status_code=201)
async def create_event(data: ScheduleEventCreate, db: DbSession, current_user: CurrentUser):
    event = ScheduleEvent(**data.model_dump())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=ScheduleEventResponse)
async def update_event(event_id: UUID, data: ScheduleEventUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(ScheduleEvent).where(ScheduleEvent.id == event_id))
    event = result.scalars().first()
    if not event:
        raise NotFoundError("ScheduleEvent", str(event_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}")
async def delete_event(event_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(ScheduleEvent).where(ScheduleEvent.id == event_id))
    event = result.scalars().first()
    if not event:
        raise NotFoundError("ScheduleEvent", str(event_id))
    await db.delete(event)
    await db.commit()
    return {"message": "Event deleted"}
