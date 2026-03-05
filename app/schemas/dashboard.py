from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_customers: int
    active_jobs: int
    revenue_mtd: float
    revenue_ytd: float
    upcoming_jobs: int
    overdue_invoices: int
    low_stock_count: int
    crew_utilization: float


class RevenueReport(BaseModel):
    period: str
    revenue: float
    expenses: float
    profit: float


class JobProfitabilityReport(BaseModel):
    job_type: str
    job_count: int
    total_revenue: float
    avg_duration_hours: float


class CrewPerformanceReport(BaseModel):
    crew_id: str
    crew_name: str
    jobs_completed: int
    total_hours: float
    avg_rating: float


class CustomerLTVReport(BaseModel):
    customer_id: str
    customer_name: str
    total_spent: float
    job_count: int
    first_job_date: str | None
    last_job_date: str | None
