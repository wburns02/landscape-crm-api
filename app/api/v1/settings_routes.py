from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.settings import SystemSettings
from app.schemas.settings import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings(db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalars().first()
    if not settings:
        # Create default settings
        settings = SystemSettings(
            company_name="GreenScape Landscaping",
            company_phone="(512) 555-0100",
            company_email="info@greenscapelandscaping.com",
            company_address="1234 Oak Valley Dr, Austin, TX 78745",
            tax_rate=8.25,
            default_payment_terms_days=30,
            business_hours={
                "monday": {"open": "07:00", "close": "18:00"},
                "tuesday": {"open": "07:00", "close": "18:00"},
                "wednesday": {"open": "07:00", "close": "18:00"},
                "thursday": {"open": "07:00", "close": "18:00"},
                "friday": {"open": "07:00", "close": "17:00"},
                "saturday": {"open": "08:00", "close": "14:00"},
                "sunday": "closed",
            },
            service_area={"radius_miles": 35, "center": "Austin, TX"},
            pricing_templates=[
                {"service": "Weekly Mowing (1/4 acre)", "price": 55},
                {"service": "Weekly Mowing (1/2 acre)", "price": 85},
                {"service": "Weekly Mowing (1 acre)", "price": 125},
                {"service": "Mulch Installation (per yard)", "price": 85},
                {"service": "Tree Trimming (per hour)", "price": 150},
                {"service": "Irrigation Repair (per hour)", "price": 95},
                {"service": "Spring Cleanup", "price": 250},
                {"service": "Fall Cleanup", "price": 275},
                {"service": "Sod Installation (per sqft)", "price": 2.50},
                {"service": "Landscape Design Consultation", "price": 200},
            ],
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.patch("", response_model=SettingsResponse)
async def update_settings(data: SettingsUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalars().first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)
    await db.commit()
    await db.refresh(settings)
    return settings
