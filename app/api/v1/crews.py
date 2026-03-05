from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError
from app.models.crew import Crew, CrewMember
from app.schemas.crew import CrewCreate, CrewMemberCreate, CrewMemberResponse, CrewResponse, CrewUpdate

router = APIRouter(prefix="/crews", tags=["crews"])


@router.get("", response_model=list[CrewResponse])
async def list_crews(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    result = await db.execute(
        select(Crew).order_by(Crew.name.asc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/{crew_id}", response_model=CrewResponse)
async def get_crew(crew_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    crew = result.scalars().first()
    if not crew:
        raise NotFoundError("Crew", str(crew_id))
    return crew


@router.post("", response_model=CrewResponse, status_code=201)
async def create_crew(data: CrewCreate, db: DbSession, current_user: CurrentUser):
    crew = Crew(**data.model_dump())
    db.add(crew)
    await db.commit()
    await db.refresh(crew)
    return crew


@router.patch("/{crew_id}", response_model=CrewResponse)
async def update_crew(crew_id: UUID, data: CrewUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    crew = result.scalars().first()
    if not crew:
        raise NotFoundError("Crew", str(crew_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(crew, key, value)
    await db.commit()
    await db.refresh(crew)
    return crew


@router.delete("/{crew_id}")
async def delete_crew(crew_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    crew = result.scalars().first()
    if not crew:
        raise NotFoundError("Crew", str(crew_id))
    await db.delete(crew)
    await db.commit()
    return {"message": "Crew deleted"}


@router.get("/{crew_id}/members", response_model=list[CrewMemberResponse])
async def get_crew_members(crew_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(CrewMember).where(CrewMember.crew_id == crew_id).order_by(CrewMember.joined_at.asc())
    )
    return result.scalars().all()


@router.post("/{crew_id}/members", response_model=CrewMemberResponse, status_code=201)
async def add_crew_member(crew_id: UUID, data: CrewMemberCreate, db: DbSession, current_user: CurrentUser):
    # Verify crew exists
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    if not result.scalars().first():
        raise NotFoundError("Crew", str(crew_id))

    member = CrewMember(crew_id=crew_id, user_id=data.user_id, role=data.role)
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/{crew_id}/members/{member_id}")
async def remove_crew_member(crew_id: UUID, member_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(CrewMember).where(CrewMember.id == member_id, CrewMember.crew_id == crew_id)
    )
    member = result.scalars().first()
    if not member:
        raise NotFoundError("CrewMember", str(member_id))
    await db.delete(member)
    await db.commit()
    return {"message": "Member removed"}
