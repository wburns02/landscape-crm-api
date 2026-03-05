from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.contract import Contract
from app.models.customer import Customer
from app.models.job import Job
from app.schemas.contract import ContractCreate, ContractResponse, ContractUpdate
from app.schemas.job import JobResponse

router = APIRouter(prefix="/contracts", tags=["contracts"])

FREQUENCY_DAYS = {
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
    "quarterly": 90,
    "seasonal": 90,
}


@router.get("", response_model=list[ContractResponse])
async def list_contracts(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = None,
    customer_id: UUID | None = None,
):
    query = select(Contract)
    if status:
        query = query.where(Contract.status == status)
    if customer_id:
        query = query.where(Contract.customer_id == customer_id)
    query = query.order_by(Contract.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalars().first()
    if not contract:
        raise NotFoundError("Contract", str(contract_id))
    return contract


@router.post("", response_model=ContractResponse, status_code=201)
async def create_contract(data: ContractCreate, db: DbSession, current_user: CurrentUser):
    contract = Contract(**data.model_dump())
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return contract


@router.patch("/{contract_id}", response_model=ContractResponse)
async def update_contract(contract_id: UUID, data: ContractUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalars().first()
    if not contract:
        raise NotFoundError("Contract", str(contract_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(contract, key, value)
    await db.commit()
    await db.refresh(contract)
    return contract


@router.post("/{contract_id}/generate-jobs", response_model=list[JobResponse])
async def generate_jobs(contract_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalars().first()
    if not contract:
        raise NotFoundError("Contract", str(contract_id))
    if contract.status != "active":
        raise ValidationError("Contract must be active to generate jobs")

    # Get customer for address
    cust_result = await db.execute(select(Customer).where(Customer.id == contract.customer_id))
    customer = cust_result.scalars().first()

    start = date.fromisoformat(contract.start_date) if contract.start_date else date.today()
    end = date.fromisoformat(contract.end_date) if contract.end_date else start + timedelta(days=365)
    interval = FREQUENCY_DAYS.get(contract.visit_frequency, 7)

    services = contract.services or [{"description": "Maintenance visit"}]
    service_desc = ", ".join(s.get("description", "Service") for s in services)

    jobs = []
    current = start
    while current <= end:
        job = Job(
            customer_id=contract.customer_id,
            title=f"{contract.title} - {current.isoformat()}",
            description=service_desc,
            job_type="maintenance",
            status="scheduled",
            priority="normal",
            scheduled_date=current.isoformat(),
            estimated_duration_hours=1.5,
            address=customer.address if customer else None,
            lat=customer.lat if customer else None,
            lng=customer.lng if customer else None,
            is_recurring=True,
            recurrence_rule=contract.visit_frequency,
        )
        db.add(job)
        jobs.append(job)
        current += timedelta(days=interval)

    await db.commit()
    for j in jobs:
        await db.refresh(j)
    return jobs


@router.delete("/{contract_id}")
async def delete_contract(contract_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalars().first()
    if not contract:
        raise NotFoundError("Contract", str(contract_id))
    await db.delete(contract)
    await db.commit()
    return {"message": "Contract deleted"}
