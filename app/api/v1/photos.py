from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError
from app.models.photo import Photo
from app.schemas.photo import PhotoCreate, PhotoResponse, PhotoUpdate

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("", response_model=list[PhotoResponse])
async def list_photos(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    job_id: UUID | None = None,
    customer_id: UUID | None = None,
    photo_type: str | None = None,
):
    query = select(Photo)
    if job_id:
        query = query.where(Photo.job_id == job_id)
    if customer_id:
        query = query.where(Photo.customer_id == customer_id)
    if photo_type:
        query = query.where(Photo.photo_type == photo_type)
    query = query.order_by(Photo.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise NotFoundError("Photo", str(photo_id))
    return photo


@router.post("", response_model=PhotoResponse, status_code=201)
async def create_photo(data: PhotoCreate, db: DbSession, current_user: CurrentUser):
    photo = Photo(**data.model_dump())
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


@router.patch("/{photo_id}", response_model=PhotoResponse)
async def update_photo(photo_id: UUID, data: PhotoUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise NotFoundError("Photo", str(photo_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(photo, key, value)
    await db.commit()
    await db.refresh(photo)
    return photo


@router.delete("/{photo_id}")
async def delete_photo(photo_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise NotFoundError("Photo", str(photo_id))
    await db.delete(photo)
    await db.commit()
    return {"message": "Photo deleted"}
