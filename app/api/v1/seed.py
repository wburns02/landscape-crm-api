from fastapi import APIRouter

from app.api.deps import DbSession
from app.seed_data import seed

router = APIRouter(tags=["seed"])


@router.post("/seed")
async def seed_database(db: DbSession):
    """Populate the database with realistic demo data."""
    result = await seed(db)
    return {"message": "Database seeded successfully", "counts": result}
