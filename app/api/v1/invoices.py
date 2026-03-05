import random
import string
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate, RecordPaymentRequest
from app.schemas.payment import PaymentResponse

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = None,
    customer_id: UUID | None = None,
):
    query = select(Invoice)
    if status:
        query = query.where(Invoice.status == status)
    if customer_id:
        query = query.where(Invoice.customer_id == customer_id)
    query = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise NotFoundError("Invoice", str(invoice_id))
    return invoice


@router.post("", response_model=InvoiceResponse, status_code=201)
async def create_invoice(data: InvoiceCreate, db: DbSession, current_user: CurrentUser):
    dump = data.model_dump()
    if not dump.get("invoice_number"):
        rand = "".join(random.choices(string.digits, k=4))
        dump["invoice_number"] = f"INV-{rand}"
    # Auto-calculate totals
    line_items = dump.get("line_items") or []
    subtotal = sum(item.get("total", item.get("quantity", 0) * item.get("unit_price", 0)) for item in line_items)
    tax_rate = dump.get("tax_rate", 8.25)
    tax_amount = round(subtotal * tax_rate / 100, 2)
    dump["subtotal"] = round(subtotal, 2)
    dump["tax_amount"] = tax_amount
    dump["total"] = round(subtotal + tax_amount, 2)

    invoice = Invoice(**dump)
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(invoice_id: UUID, data: InvoiceUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise NotFoundError("Invoice", str(invoice_id))
    updates = data.model_dump(exclude_unset=True)
    if "line_items" in updates:
        line_items = updates["line_items"] or []
        subtotal = sum(item.get("total", item.get("quantity", 0) * item.get("unit_price", 0)) for item in line_items)
        tax_rate = updates.get("tax_rate", invoice.tax_rate)
        tax_amount = round(subtotal * tax_rate / 100, 2)
        updates["subtotal"] = round(subtotal, 2)
        updates["tax_amount"] = tax_amount
        updates["total"] = round(subtotal + tax_amount, 2)
    for key, value in updates.items():
        setattr(invoice, key, value)
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
async def send_invoice(invoice_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise NotFoundError("Invoice", str(invoice_id))
    invoice.status = "sent"
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.post("/{invoice_id}/record-payment", response_model=PaymentResponse)
async def record_payment(invoice_id: UUID, data: RecordPaymentRequest, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise NotFoundError("Invoice", str(invoice_id))

    payment = Payment(
        invoice_id=invoice_id,
        amount=data.amount,
        method=data.method,
        reference_number=data.reference_number,
        notes=data.notes,
        paid_at=datetime.now(timezone.utc),
    )
    db.add(payment)

    invoice.paid_amount = (invoice.paid_amount or 0) + data.amount
    if invoice.paid_amount >= invoice.total:
        invoice.status = "paid"
        invoice.paid_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(payment)
    return payment


@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise NotFoundError("Invoice", str(invoice_id))
    await db.delete(invoice)
    await db.commit()
    return {"message": "Invoice deleted"}
