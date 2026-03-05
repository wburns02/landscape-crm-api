from datetime import date, datetime, timezone

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models.customer import Customer
from app.models.inventory_item import InventoryItem
from app.models.invoice import Invoice
from app.models.job import Job
from app.models.payment import Payment
from app.models.time_entry import TimeEntry
from app.schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: DbSession, current_user: CurrentUser):
    # Total customers
    result = await db.execute(select(func.count(Customer.id)))
    total_customers = result.scalar() or 0

    # Active jobs (pending, scheduled, in_progress)
    result = await db.execute(
        select(func.count(Job.id)).where(Job.status.in_(["pending", "scheduled", "in_progress"]))
    )
    active_jobs = result.scalar() or 0

    # Revenue MTD
    today = date.today()
    mtd_start = date(today.year, today.month, 1)
    result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(Payment.paid_at >= datetime(mtd_start.year, mtd_start.month, mtd_start.day, tzinfo=timezone.utc))
    )
    revenue_mtd = float(result.scalar() or 0)

    # Revenue YTD
    ytd_start = date(today.year, 1, 1)
    result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(Payment.paid_at >= datetime(ytd_start.year, ytd_start.month, ytd_start.day, tzinfo=timezone.utc))
    )
    revenue_ytd = float(result.scalar() or 0)

    # Upcoming jobs (next 7 days)
    from datetime import timedelta
    end_date = today + timedelta(days=7)
    result = await db.execute(
        select(func.count(Job.id))
        .where(Job.scheduled_date >= today)
        .where(Job.scheduled_date <= end_date)
        .where(Job.status.in_(["pending", "scheduled"]))
    )
    upcoming_jobs = result.scalar() or 0

    # Overdue invoices
    result = await db.execute(
        select(func.count(Invoice.id))
        .where(Invoice.status == "sent")
        .where(Invoice.due_date < today)
    )
    overdue_invoices = result.scalar() or 0

    # Low stock count
    result = await db.execute(
        select(func.count(InventoryItem.id))
        .where(InventoryItem.is_active == True)
        .where(InventoryItem.quantity_on_hand <= InventoryItem.reorder_level)
    )
    low_stock_count = result.scalar() or 0

    # Crew utilization (% of logged hours vs 8hr workday * workdays this month)
    result = await db.execute(
        select(func.coalesce(func.sum(TimeEntry.hours), 0))
        .where(TimeEntry.clock_in >= datetime(mtd_start.year, mtd_start.month, mtd_start.day, tzinfo=timezone.utc))
    )
    total_hours = float(result.scalar() or 0)
    workdays_so_far = max(sum(1 for d in range(1, today.day + 1) if date(today.year, today.month, d).weekday() < 5), 1)
    # Assume 5 crew members, 8 hours each
    capacity = workdays_so_far * 5 * 8
    crew_utilization = round(min((total_hours / capacity) * 100, 100), 1) if capacity > 0 else 0

    return DashboardResponse(
        total_customers=total_customers,
        active_jobs=active_jobs,
        revenue_mtd=round(revenue_mtd, 2),
        revenue_ytd=round(revenue_ytd, 2),
        upcoming_jobs=upcoming_jobs,
        overdue_invoices=overdue_invoices,
        low_stock_count=low_stock_count,
        crew_utilization=crew_utilization,
    )
