from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate, EquipmentResponse, EquipmentStatusUpdate, EquipmentUpdate

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("", response_model=list[EquipmentResponse])
async def list_equipment(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    equipment_type: str | None = None,
    status: str | None = None,
):
    query = select(Equipment)
    if equipment_type:
        query = query.where(Equipment.equipment_type == equipment_type)
    if status:
        query = query.where(Equipment.status == status)
    query = query.order_by(Equipment.name.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/maintenance-due", response_model=list[EquipmentResponse])
async def get_maintenance_due(db: DbSession, current_user: CurrentUser):
    today = date.today().isoformat()
    result = await db.execute(
        select(Equipment)
        .where(Equipment.next_maintenance_date != None)
        .where(Equipment.next_maintenance_date <= today)
        .where(Equipment.status != "retired")
        .order_by(Equipment.next_maintenance_date.asc())
    )
    return result.scalars().all()


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(equipment_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    eq = result.scalars().first()
    if not eq:
        raise NotFoundError("Equipment", str(equipment_id))
    return eq


@router.post("", response_model=EquipmentResponse, status_code=201)
async def create_equipment(data: EquipmentCreate, db: DbSession, current_user: CurrentUser):
    eq = Equipment(**data.model_dump())
    db.add(eq)
    await db.commit()
    await db.refresh(eq)
    return eq


@router.patch("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(equipment_id: UUID, data: EquipmentUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    eq = result.scalars().first()
    if not eq:
        raise NotFoundError("Equipment", str(equipment_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(eq, key, value)
    await db.commit()
    await db.refresh(eq)
    return eq


@router.patch("/{equipment_id}/status", response_model=EquipmentResponse)
async def update_equipment_status(equipment_id: UUID, data: EquipmentStatusUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    eq = result.scalars().first()
    if not eq:
        raise NotFoundError("Equipment", str(equipment_id))
    valid = ["available", "in_use", "maintenance", "retired"]
    if data.status not in valid:
        raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid)}")
    eq.status = data.status
    await db.commit()
    await db.refresh(eq)
    return eq


@router.delete("/{equipment_id}")
async def delete_equipment(equipment_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    eq = result.scalars().first()
    if not eq:
        raise NotFoundError("Equipment", str(equipment_id))
    await db.delete(eq)
    await db.commit()
    return {"message": "Equipment deleted"}
