import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import all models so Base.metadata knows about them
    from app.models import (  # noqa: F401
        Contract,
        Crew,
        CrewMember,
        Customer,
        DirectMailCampaign,
        DirectMailRecipient,
        EmailCampaign,
        EmailCampaignRecipient,
        EmailSend,
        EmailTemplate,
        Equipment,
        InventoryItem,
        Invoice,
        Job,
        Lead,
        MailTemplate,
        Payment,
        Photo,
        Prospect,
        ScheduleEvent,
        SystemSettings,
        TimeEntry,
        User,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="GreenScape CRM API",
    description="Complete backend API for Landscape & Nursery CRM",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — build origins list, stripping trailing slashes
_origins = [
    settings.FRONTEND_URL.rstrip("/"),
    "http://localhost:5173",
    "http://localhost:5176",
    "http://localhost:3000",
]
# Add extra CORS origins (comma-separated) if set
_extra = os.environ.get("EXTRA_CORS_ORIGINS", "")
if _extra:
    _origins.extend(o.strip().rstrip("/") for o in _extra.split(",") if o.strip())
# Filter out empty strings
_origins = [o for o in _origins if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# GZip
app.add_middleware(GZipMiddleware, minimum_size=500)

# Register routers
from app.api.v1.auth import router as auth_router
from app.api.v1.contracts import router as contracts_router
from app.api.v1.crews import router as crews_router
from app.api.v1.customers import router as customers_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.equipment import router as equipment_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.leads import router as leads_router
from app.api.v1.photos import router as photos_router
from app.api.v1.quotes import router as quotes_router
from app.api.v1.reports import router as reports_router
from app.api.v1.schedule import router as schedule_router
from app.api.v1.prospects import router as prospects_router
from app.api.v1.email import router as email_router
from app.api.v1.seed import router as seed_router
from app.api.v1.settings_routes import router as settings_router
from app.api.v1.time_entries import router as time_entries_router
from app.api.v1.direct_mail import router as direct_mail_router

PREFIX = "/api/v1"
app.include_router(auth_router, prefix=PREFIX)
app.include_router(customers_router, prefix=PREFIX)
app.include_router(jobs_router, prefix=PREFIX)
app.include_router(schedule_router, prefix=PREFIX)
app.include_router(inventory_router, prefix=PREFIX)
app.include_router(quotes_router, prefix=PREFIX)
app.include_router(invoices_router, prefix=PREFIX)
app.include_router(contracts_router, prefix=PREFIX)
app.include_router(crews_router, prefix=PREFIX)
app.include_router(equipment_router, prefix=PREFIX)
app.include_router(time_entries_router, prefix=PREFIX)
app.include_router(leads_router, prefix=PREFIX)
app.include_router(photos_router, prefix=PREFIX)
app.include_router(dashboard_router, prefix=PREFIX)
app.include_router(reports_router, prefix=PREFIX)
app.include_router(prospects_router, prefix=PREFIX)
app.include_router(email_router, prefix=PREFIX)
app.include_router(settings_router, prefix=PREFIX)
app.include_router(direct_mail_router, prefix=PREFIX)
app.include_router(seed_router, prefix=PREFIX)


@app.get("/ping")
async def health_check():
    return {
        "status": "healthy",
        "service": "GreenScape CRM API",
        "version": "1.0.0",
        "cors_origins": _origins,
    }
