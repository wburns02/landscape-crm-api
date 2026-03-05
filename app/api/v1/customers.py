from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.job import Job
from app.models.photo import Photo
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.schemas.invoice import InvoiceResponse
from app.schemas.job import JobResponse
from app.schemas.photo import PhotoResponse

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerResponse])
async def list_customers(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = None,
    customer_type: str | None = None,
):
    query = select(Customer)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (Customer.first_name.ilike(pattern))
            | (Customer.last_name.ilike(pattern))
            | (Customer.company_name.ilike(pattern))
            | (Customer.email.ilike(pattern))
            | (Customer.phone.ilike(pattern))
        )
    if customer_type:
        query = query.where(Customer.customer_type == customer_type)
    query = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise NotFoundError("Customer", str(customer_id))
    return customer


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(data: CustomerCreate, db: DbSession, current_user: CurrentUser):
    customer = Customer(**data.model_dump())
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: UUID, data: CustomerUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise NotFoundError("Customer", str(customer_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
async def delete_customer(customer_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise NotFoundError("Customer", str(customer_id))
    await db.delete(customer)
    await db.commit()
    return {"message": "Customer deleted"}


@router.get("/{customer_id}/jobs", response_model=list[JobResponse])
async def get_customer_jobs(customer_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(Job).where(Job.customer_id == customer_id).order_by(Job.scheduled_date.desc())
    )
    return result.scalars().all()


@router.get("/{customer_id}/invoices", response_model=list[InvoiceResponse])
async def get_customer_invoices(customer_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(Invoice).where(Invoice.customer_id == customer_id).order_by(Invoice.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{customer_id}/photos", response_model=list[PhotoResponse])
async def get_customer_photos(customer_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(Photo).where(Photo.customer_id == customer_id).order_by(Photo.created_at.desc())
    )
    return result.scalars().all()
