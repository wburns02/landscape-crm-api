from fastapi import APIRouter

from app.api.deps import DbSession
from app.seed_data import seed

router = APIRouter(tags=["seed"])


@router.post("/seed")
async def seed_database(db: DbSession):
    """Populate the database with realistic demo data."""
    result = await seed(db)
    return {"message": "Database seeded successfully", "counts": result}


@router.post("/seed/templates")
async def seed_email_templates(db: DbSession):
    """Seed starter email templates."""
    from sqlalchemy import select
    from app.models.email_campaign import EmailTemplate
    from app.seed_templates import TEMPLATES

    created = 0
    for t in TEMPLATES:
        existing = await db.execute(
            select(EmailTemplate).where(EmailTemplate.name == t["name"])
        )
        if existing.scalars().first():
            continue
        template = EmailTemplate(**t)
        db.add(template)
        created += 1

    await db.commit()
    return {"message": f"Seeded {created} email templates", "created": created}
