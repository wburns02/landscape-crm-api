from datetime import date

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models.crew import Crew
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.job import Job
from app.models.payment import Payment
from app.models.time_entry import TimeEntry
from app.schemas.dashboard import (
    CrewPerformanceReport,
    CustomerLTVReport,
    JobProfitabilityReport,
    RevenueReport,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/revenue", response_model=list[RevenueReport])
async def revenue_report(
    db: DbSession,
    current_user: CurrentUser,
    year: int = Query(default=None),
):
    if not year:
        year = date.today().year

    reports = []
    for month in range(1, 13):
        month_start = f"{year}-{month:02d}-01"
        if month < 12:
            month_end = f"{year}-{month + 1:02d}-01"
        else:
            month_end = f"{year + 1}-01-01"

        result = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(Payment.paid_at >= month_start)
            .where(Payment.paid_at < month_end)
        )
        revenue = float(result.scalar() or 0)

        # Estimate expenses as 60% of revenue (simplified)
        expenses = round(revenue * 0.6, 2)
        profit = round(revenue - expenses, 2)

        reports.append(
            RevenueReport(
                period=f"{year}-{month:02d}",
                revenue=round(revenue, 2),
                expenses=expenses,
                profit=profit,
            )
        )
    return reports


@router.get("/job-profitability", response_model=list[JobProfitabilityReport])
async def job_profitability(db: DbSession, current_user: CurrentUser):
    job_types = ["maintenance", "installation", "cleanup", "irrigation", "hardscaping", "tree_care", "lawn_care", "planting", "other"]
    reports = []

    for jt in job_types:
        result = await db.execute(
            select(
                func.count(Job.id),
                func.coalesce(func.avg(Job.actual_duration_hours), 0),
            ).where(Job.job_type == jt).where(Job.status == "completed")
        )
        row = result.one()
        job_count = row[0] or 0
        avg_dur = float(row[1] or 0)

        # Get revenue from invoices linked to these jobs
        result2 = await db.execute(
            select(func.coalesce(func.sum(Invoice.total), 0))
            .where(Invoice.job_id.in_(select(Job.id).where(Job.job_type == jt)))
        )
        total_revenue = float(result2.scalar() or 0)

        if job_count > 0:
            reports.append(
                JobProfitabilityReport(
                    job_type=jt,
                    job_count=job_count,
                    total_revenue=round(total_revenue, 2),
                    avg_duration_hours=round(avg_dur, 2),
                )
            )

    return reports


@router.get("/crew-performance", response_model=list[CrewPerformanceReport])
async def crew_performance(db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Crew).where(Crew.is_active == True))
    crews = result.scalars().all()

    reports = []
    for crew in crews:
        # Jobs completed by this crew
        job_result = await db.execute(
            select(func.count(Job.id))
            .where(Job.crew_id == crew.id)
            .where(Job.status == "completed")
        )
        jobs_completed = job_result.scalar() or 0

        # Total hours from time entries for crew members
        from app.models.crew import CrewMember
        member_ids_result = await db.execute(
            select(CrewMember.user_id).where(CrewMember.crew_id == crew.id)
        )
        member_ids = [r[0] for r in member_ids_result.all()]

        total_hours = 0.0
        if member_ids:
            hours_result = await db.execute(
                select(func.coalesce(func.sum(TimeEntry.hours), 0))
                .where(TimeEntry.user_id.in_(member_ids))
            )
            total_hours = float(hours_result.scalar() or 0)

        reports.append(
            CrewPerformanceReport(
                crew_id=str(crew.id),
                crew_name=crew.name,
                jobs_completed=jobs_completed,
                total_hours=round(total_hours, 2),
                avg_rating=4.5,  # Placeholder until rating system implemented
            )
        )

    return reports


@router.get("/customer-lifetime-value", response_model=list[CustomerLTVReport])
async def customer_ltv(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
):
    result = await db.execute(
        select(Customer)
        .order_by(Customer.total_spent.desc())
        .limit(limit)
    )
    customers = result.scalars().all()

    reports = []
    for c in customers:
        # Get first and last job dates
        first_result = await db.execute(
            select(func.min(Job.scheduled_date)).where(Job.customer_id == c.id)
        )
        last_result = await db.execute(
            select(func.max(Job.scheduled_date)).where(Job.customer_id == c.id)
        )
        first_job = first_result.scalar()
        last_job = last_result.scalar()

        reports.append(
            CustomerLTVReport(
                customer_id=str(c.id),
                customer_name=f"{c.first_name} {c.last_name}",
                total_spent=c.total_spent,
                job_count=c.job_count,
                first_job_date=first_job,
                last_job_date=last_job,
            )
        )

    return reports
