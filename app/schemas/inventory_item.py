from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InventoryItemBase(BaseModel):
    name: str
    category: str = "other"
    sku: str | None = None
    description: str | None = None
    unit: str = "each"
    quantity_on_hand: float = 0
    reorder_level: float = 0
    unit_cost: float = 0
    unit_price: float = 0
    supplier_name: str | None = None
    supplier_contact: str | None = None
    lot_number: str | None = None
    location: str | None = None
    image_url: str | None = None
    is_active: bool = True


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    sku: str | None = None
    description: str | None = None
    unit: str | None = None
    quantity_on_hand: float | None = None
    reorder_level: float | None = None
    unit_cost: float | None = None
    unit_price: float | None = None
    supplier_name: str | None = None
    supplier_contact: str | None = None
    lot_number: str | None = None
    location: str | None = None
    image_url: str | None = None
    is_active: bool | None = None


class QuantityAdjust(BaseModel):
    adjustment: float
    reason: str | None = None


class InventoryItemResponse(InventoryItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
