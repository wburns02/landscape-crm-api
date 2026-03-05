from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadResponse, LeadStatusUpdate, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=list[LeadResponse])
async def list_leads(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = None,
    source: str | None = None,
    search: str | None = None,
):
    query = select(Lead)
    if status:
        query = query.where(Lead.status == status)
    if source:
        query = query.where(Lead.source == source)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (Lead.first_name.ilike(pattern))
            | (Lead.last_name.ilike(pattern))
            | (Lead.email.ilike(pattern))
            | (Lead.phone.ilike(pattern))
        )
    query = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalars().first()
    if not lead:
        raise NotFoundError("Lead", str(lead_id))
    return lead


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(data: LeadCreate, db: DbSession, current_user: CurrentUser):
    lead = Lead(**data.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: UUID, data: LeadUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalars().first()
    if not lead:
        raise NotFoundError("Lead", str(lead_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.patch("/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(lead_id: UUID, data: LeadStatusUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalars().first()
    if not lead:
        raise NotFoundError("Lead", str(lead_id))
    valid = ["new", "contacted", "qualified", "quoted", "won", "lost"]
    if data.status not in valid:
        raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid)}")
    lead.status = data.status
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
async def delete_lead(lead_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalars().first()
    if not lead:
        raise NotFoundError("Lead", str(lead_id))
    await db.delete(lead)
    await db.commit()
    return {"message": "Lead deleted"}
