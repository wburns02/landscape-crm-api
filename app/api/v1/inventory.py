from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError
from app.models.inventory_item import InventoryItem
from app.schemas.inventory_item import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
    QuantityAdjust,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryItemResponse])
async def list_inventory(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category: str | None = None,
    search: str | None = None,
):
    query = select(InventoryItem).where(InventoryItem.is_active == True)
    if category:
        query = query.where(InventoryItem.category == category)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (InventoryItem.name.ilike(pattern))
            | (InventoryItem.sku.ilike(pattern))
            | (InventoryItem.description.ilike(pattern))
        )
    query = query.order_by(InventoryItem.name.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/low-stock", response_model=list[InventoryItemResponse])
async def get_low_stock(db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.is_active == True)
        .where(InventoryItem.quantity_on_hand <= InventoryItem.reorder_level)
        .order_by(InventoryItem.quantity_on_hand.asc())
    )
    return result.scalars().all()


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_item(item_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise NotFoundError("InventoryItem", str(item_id))
    return item


@router.post("", response_model=InventoryItemResponse, status_code=201)
async def create_item(data: InventoryItemCreate, db: DbSession, current_user: CurrentUser):
    item = InventoryItem(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=InventoryItemResponse)
async def update_item(item_id: UUID, data: InventoryItemUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise NotFoundError("InventoryItem", str(item_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{item_id}/adjust-quantity", response_model=InventoryItemResponse)
async def adjust_quantity(item_id: UUID, data: QuantityAdjust, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise NotFoundError("InventoryItem", str(item_id))
    item.quantity_on_hand += data.adjustment
    if item.quantity_on_hand < 0:
        item.quantity_on_hand = 0
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_item(item_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise NotFoundError("InventoryItem", str(item_id))
    await db.delete(item)
    await db.commit()
    return {"message": "Item deleted"}
