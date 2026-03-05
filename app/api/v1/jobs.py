from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError
from app.models.job import Job
from app.models.photo import Photo
from app.schemas.job import JobCreate, JobResponse, JobStatusUpdate, JobUpdate
from app.schemas.photo import PhotoCreate, PhotoResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = None,
    job_type: str | None = None,
    customer_id: UUID | None = None,
    crew_id: UUID | None = None,
):
    query = select(Job)
    if status:
        query = query.where(Job.status == status)
    if job_type:
        query = query.where(Job.job_type == job_type)
    if customer_id:
        query = query.where(Job.customer_id == customer_id)
    if crew_id:
        query = query.where(Job.crew_id == crew_id)
    query = query.order_by(Job.scheduled_date.desc().nullslast(), Job.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/upcoming", response_model=list[JobResponse])
async def get_upcoming_jobs(
    db: DbSession,
    current_user: CurrentUser,
    days: int = Query(7, ge=1, le=90),
):
    today = date.today().isoformat()
    end = date.today().replace(day=date.today().day)
    from datetime import timedelta

    end_date = (date.today() + timedelta(days=days)).isoformat()
    result = await db.execute(
        select(Job)
        .where(Job.scheduled_date >= today)
        .where(Job.scheduled_date <= end_date)
        .where(Job.status.in_(["pending", "scheduled"]))
        .order_by(Job.scheduled_date.asc())
    )
    return result.scalars().all()


@router.get("/by-crew/{crew_id}", response_model=list[JobResponse])
async def get_jobs_by_crew(crew_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(Job).where(Job.crew_id == crew_id).order_by(Job.scheduled_date.desc().nullslast())
    )
    return result.scalars().all()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise NotFoundError("Job", str(job_id))
    return job


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(data: JobCreate, db: DbSession, current_user: CurrentUser):
    job = Job(**data.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(job_id: UUID, data: JobUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise NotFoundError("Job", str(job_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(job, key, value)
    await db.commit()
    await db.refresh(job)
    return job


@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_job_status(job_id: UUID, data: JobStatusUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise NotFoundError("Job", str(job_id))
    valid_statuses = ["pending", "scheduled", "in_progress", "completed", "invoiced", "cancelled"]
    if data.status not in valid_statuses:
        from app.exceptions import ValidationError
        raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    job.status = data.status
    await db.commit()
    await db.refresh(job)
    return job


@router.delete("/{job_id}")
async def delete_job(job_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise NotFoundError("Job", str(job_id))
    await db.delete(job)
    await db.commit()
    return {"message": "Job deleted"}


@router.post("/{job_id}/photos", response_model=PhotoResponse, status_code=201)
async def add_job_photo(job_id: UUID, data: PhotoCreate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise NotFoundError("Job", str(job_id))
    photo = Photo(
        job_id=job_id,
        url=data.url,
        thumbnail_url=data.thumbnail_url,
        photo_type=data.photo_type,
        caption=data.caption,
        taken_by=data.taken_by or current_user.id,
        taken_at=data.taken_at or datetime.now(timezone.utc),
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo
