import random
import string
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.invoice import Invoice
from app.models.quote import Quote
from app.schemas.invoice import InvoiceResponse
from app.schemas.quote import QuoteCreate, QuoteResponse, QuoteUpdate

router = APIRouter(prefix="/quotes", tags=["quotes"])


def generate_quote_number() -> str:
    rand = "".join(random.choices(string.digits, k=4))
    return f"Q-{rand}"


@router.get("", response_model=list[QuoteResponse])
async def list_quotes(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = None,
    customer_id: UUID | None = None,
):
    query = select(Quote)
    if status:
        query = query.where(Quote.status == status)
    if customer_id:
        query = query.where(Quote.customer_id == customer_id)
    query = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(quote_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalars().first()
    if not quote:
        raise NotFoundError("Quote", str(quote_id))
    return quote


@router.post("", response_model=QuoteResponse, status_code=201)
async def create_quote(data: QuoteCreate, db: DbSession, current_user: CurrentUser):
    dump = data.model_dump()
    if not dump.get("quote_number"):
        dump["quote_number"] = generate_quote_number()
    # Auto-calculate totals from line items
    line_items = dump.get("line_items") or []
    subtotal = sum(item.get("total", item.get("quantity", 0) * item.get("unit_price", 0)) for item in line_items)
    tax_rate = dump.get("tax_rate", 8.25)
    tax_amount = round(subtotal * tax_rate / 100, 2)
    dump["subtotal"] = round(subtotal, 2)
    dump["tax_amount"] = tax_amount
    dump["total"] = round(subtotal + tax_amount, 2)

    quote = Quote(**dump)
    db.add(quote)
    await db.commit()
    await db.refresh(quote)
    return quote


@router.patch("/{quote_id}", response_model=QuoteResponse)
async def update_quote(quote_id: UUID, data: QuoteUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalars().first()
    if not quote:
        raise NotFoundError("Quote", str(quote_id))
    updates = data.model_dump(exclude_unset=True)

    # Recalculate totals if line_items changed
    if "line_items" in updates:
        line_items = updates["line_items"] or []
        subtotal = sum(item.get("total", item.get("quantity", 0) * item.get("unit_price", 0)) for item in line_items)
        tax_rate = updates.get("tax_rate", quote.tax_rate)
        tax_amount = round(subtotal * tax_rate / 100, 2)
        updates["subtotal"] = round(subtotal, 2)
        updates["tax_amount"] = tax_amount
        updates["total"] = round(subtotal + tax_amount, 2)

    for key, value in updates.items():
        setattr(quote, key, value)
    await db.commit()
    await db.refresh(quote)
    return quote


@router.post("/{quote_id}/send", response_model=QuoteResponse)
async def send_quote(quote_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalars().first()
    if not quote:
        raise NotFoundError("Quote", str(quote_id))
    quote.status = "sent"
    quote.sent_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(quote)
    return quote


@router.post("/{quote_id}/convert-to-invoice", response_model=InvoiceResponse)
async def convert_to_invoice(quote_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalars().first()
    if not quote:
        raise NotFoundError("Quote", str(quote_id))
    if quote.status not in ("sent", "accepted"):
        raise ValidationError("Quote must be sent or accepted to convert to invoice")

    quote.status = "accepted"
    quote.accepted_at = datetime.now(timezone.utc)

    rand = "".join(random.choices(string.digits, k=4))
    invoice = Invoice(
        customer_id=quote.customer_id,
        quote_id=quote.id,
        invoice_number=f"INV-{rand}",
        status="draft",
        line_items=quote.line_items,
        subtotal=quote.subtotal,
        tax_rate=quote.tax_rate,
        tax_amount=quote.tax_amount,
        total=quote.total,
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.delete("/{quote_id}")
async def delete_quote(quote_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalars().first()
    if not quote:
        raise NotFoundError("Quote", str(quote_id))
    await db.delete(quote)
    await db.commit()
    return {"message": "Quote deleted"}
