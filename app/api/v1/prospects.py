import csv
import uuid as uuid_mod
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import func, select, text

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.lead import Lead
from app.models.prospect import Prospect
from app.schemas.prospect import (
    ImportResult,
    ProspectCreate,
    ProspectListResponse,
    ProspectResponse,
    ProspectUpdate,
)

router = APIRouter(prefix="/prospects", tags=["prospects"])

AUSTIN_METRO_CITIES = {
    "austin", "bee cave", "lakeway", "west lake hills", "pflugerville",
    "del valle", "rollingwood", "the hills", "sunset valley", "manor",
    "round rock", "cedar park", "creedmoor", "leander", "georgetown",
    "dripping springs", "buda", "kyle", "san marcos", "bastrop",
    "elgin", "taylor", "hutto", "city of austin",
}

CSV_PATH = "/mnt/win11/Fedora/crown_scrapers/data/enriched/enriched_contacts.csv"


@router.get("", response_model=ProspectListResponse)
async def list_prospects(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: str | None = None,
    city: str | None = None,
    zip_code: str | None = None,
    work_type: str | None = None,
    status: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    min_property_value: float | None = None,
    max_property_value: float | None = None,
    sort_by: str = "lead_score",
    sort_dir: str = "desc",
):
    query = select(Prospect)
    count_query = select(func.count()).select_from(Prospect)

    filters = []
    if search:
        pattern = f"%{search}%"
        filters.append(
            (Prospect.full_name.ilike(pattern))
            | (Prospect.address.ilike(pattern))
            | (Prospect.phone.ilike(pattern))
            | (Prospect.email.ilike(pattern))
        )
    if city:
        filters.append(Prospect.city.ilike(city))
    if zip_code:
        filters.append(Prospect.zip_code == zip_code)
    if work_type:
        filters.append(Prospect.work_type == work_type)
    if status:
        filters.append(Prospect.status == status)
    if min_score is not None:
        filters.append(Prospect.lead_score >= min_score)
    if max_score is not None:
        filters.append(Prospect.lead_score <= max_score)
    if min_property_value is not None:
        filters.append(Prospect.property_value >= min_property_value)
    if max_property_value is not None:
        filters.append(Prospect.property_value <= max_property_value)

    for f in filters:
        query = query.where(f)
        count_query = count_query.where(f)

    # Sorting
    sort_col = getattr(Prospect, sort_by, Prospect.lead_score)
    if sort_dir == "asc":
        query = query.order_by(sort_col.asc().nullslast())
    else:
        query = query.order_by(sort_col.desc().nullslast())

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return ProspectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats")
async def prospect_stats(db: DbSession, current_user: CurrentUser):
    total = await db.execute(select(func.count()).select_from(Prospect))
    by_city = await db.execute(
        select(Prospect.city, func.count())
        .group_by(Prospect.city)
        .order_by(func.count().desc())
        .limit(20)
    )
    by_work_type = await db.execute(
        select(Prospect.work_type, func.count())
        .group_by(Prospect.work_type)
        .order_by(func.count().desc())
    )
    by_status = await db.execute(
        select(Prospect.status, func.count())
        .group_by(Prospect.status)
    )
    avg_score = await db.execute(select(func.avg(Prospect.lead_score)))
    avg_value = await db.execute(select(func.avg(Prospect.property_value)).where(Prospect.property_value > 0))

    return {
        "total": total.scalar() or 0,
        "by_city": [{"city": r[0], "count": r[1]} for r in by_city.all()],
        "by_work_type": [{"work_type": r[0], "count": r[1]} for r in by_work_type.all()],
        "by_status": [{"status": r[0], "count": r[1]} for r in by_status.all()],
        "avg_lead_score": round(avg_score.scalar() or 0, 1),
        "avg_property_value": round(avg_value.scalar() or 0, 2),
    }


@router.get("/cities")
async def prospect_cities(db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(Prospect.city, func.count())
        .where(Prospect.city.isnot(None))
        .group_by(Prospect.city)
        .order_by(func.count().desc())
    )
    return [{"city": r[0], "count": r[1]} for r in result.all()]


@router.get("/work-types")
async def prospect_work_types(db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(Prospect.work_type, func.count())
        .where(Prospect.work_type.isnot(None))
        .group_by(Prospect.work_type)
        .order_by(func.count().desc())
    )
    return [{"work_type": r[0], "count": r[1]} for r in result.all()]


@router.get("/{prospect_id}", response_model=ProspectResponse)
async def get_prospect(prospect_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
    prospect = result.scalars().first()
    if not prospect:
        raise NotFoundError("Prospect", str(prospect_id))
    return prospect


@router.post("", response_model=ProspectResponse, status_code=201)
async def create_prospect(data: ProspectCreate, db: DbSession, current_user: CurrentUser):
    d = data.model_dump()
    if not d.get("full_name"):
        d["full_name"] = f"{d['first_name']} {d['last_name']}".strip()
    prospect = Prospect(**d)
    db.add(prospect)
    await db.commit()
    await db.refresh(prospect)
    return prospect


@router.patch("/{prospect_id}", response_model=ProspectResponse)
async def update_prospect(prospect_id: UUID, data: ProspectUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
    prospect = result.scalars().first()
    if not prospect:
        raise NotFoundError("Prospect", str(prospect_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(prospect, key, value)
    if data.first_name or data.last_name:
        prospect.full_name = f"{prospect.first_name} {prospect.last_name}".strip()
    await db.commit()
    await db.refresh(prospect)
    return prospect


@router.delete("/{prospect_id}")
async def delete_prospect(prospect_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
    prospect = result.scalars().first()
    if not prospect:
        raise NotFoundError("Prospect", str(prospect_id))
    await db.delete(prospect)
    await db.commit()
    return {"message": "Prospect deleted"}


@router.post("/{prospect_id}/convert-to-lead", status_code=201)
async def convert_to_lead(prospect_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
    prospect = result.scalars().first()
    if not prospect:
        raise NotFoundError("Prospect", str(prospect_id))

    lead = Lead(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        email=prospect.email,
        phone=prospect.phone,
        address=prospect.address,
        city=prospect.city,
        state=prospect.state,
        zip_code=prospect.zip_code,
        source="import",
        status="qualified",
        notes=f"Converted from prospect. Work type: {prospect.work_type}. Score: {prospect.lead_score}",
        estimated_value=prospect.property_value,
    )
    db.add(lead)
    prospect.status = "qualified"
    await db.commit()
    await db.refresh(lead)
    return {"message": "Prospect converted to lead", "lead_id": str(lead.id)}


@router.post("/import", response_model=ImportResult)
async def import_prospects(db: DbSession, current_user: CurrentUser):
    batch_id = f"austin_import_{uuid_mod.uuid4().hex[:8]}"
    imported = 0
    skipped = 0
    errors = 0
    total = 0

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                state = (row.get("state") or "").strip().upper()
                city_raw = (row.get("city") or "").strip()
                city_lower = city_raw.lower()
                source_city = (row.get("source_city") or "").strip().lower()

                if state != "TX":
                    continue
                if city_lower not in AUSTIN_METRO_CITIES and "austin" not in source_city:
                    continue

                owner_name = (row.get("owner_name") or "").strip()
                address = (row.get("address") or "").strip()
                phone = (row.get("owner_phone") or "").strip()

                if not (owner_name and address and phone):
                    skipped += 1
                    continue

                total += 1

                # Split name
                parts = owner_name.split(None, 1)
                first_name = parts[0] if parts else owner_name
                last_name = parts[1] if len(parts) > 1 else ""

                # Parse numeric fields
                prop_val = None
                try:
                    pv = row.get("property_value", "")
                    if pv:
                        prop_val = float(pv)
                except (ValueError, TypeError):
                    pass

                sqft_val = None
                try:
                    sq = row.get("sqft", "")
                    if sq:
                        sqft_val = int(float(sq))
                except (ValueError, TypeError):
                    pass

                year_val = None
                try:
                    yb = row.get("year_built", "")
                    if yb:
                        year_val = int(float(yb))
                except (ValueError, TypeError):
                    pass

                score_val = None
                try:
                    ls = row.get("lead_score", "")
                    if ls:
                        score_val = int(float(ls))
                except (ValueError, TypeError):
                    pass

                batch.append({
                    "id": uuid_mod.uuid4(),
                    "first_name": first_name[:100],
                    "last_name": last_name[:100],
                    "full_name": owner_name[:200],
                    "phone": phone[:50],
                    "phone_2": (row.get("owner_phone_2") or "")[:50] or None,
                    "email": (row.get("owner_email") or "")[:255] or None,
                    "address": address[:500],
                    "city": city_raw[:100] or None,
                    "state": "TX",
                    "zip_code": (row.get("zip_code") or "")[:20] or None,
                    "property_value": prop_val,
                    "sqft": sqft_val,
                    "year_built": year_val,
                    "work_type": (row.get("work_type") or "")[:100] or None,
                    "lead_score": score_val,
                    "source": (row.get("source_city") or "csv_import")[:100],
                    "import_batch": batch_id,
                    "status": "new",
                    "email_status": "valid" if row.get("owner_email") else "unknown",
                    "notes": (row.get("description") or "")[:1000] or None,
                })

                if len(batch) >= 1000:
                    stmt = text("""
                        INSERT INTO prospects (id, first_name, last_name, full_name, phone, phone_2, email,
                            address, city, state, zip_code, property_value, sqft, year_built, work_type,
                            lead_score, source, import_batch, status, email_status, notes)
                        VALUES (:id, :first_name, :last_name, :full_name, :phone, :phone_2, :email,
                            :address, :city, :state, :zip_code, :property_value, :sqft, :year_built, :work_type,
                            :lead_score, :source, :import_batch, :status, :email_status, :notes)
                        ON CONFLICT (address, city, state) DO NOTHING
                    """)
                    result = await db.execute(stmt, batch)
                    imported += result.rowcount
                    skipped += len(batch) - result.rowcount
                    batch = []

            # Final batch
            if batch:
                stmt = text("""
                    INSERT INTO prospects (id, first_name, last_name, full_name, phone, phone_2, email,
                        address, city, state, zip_code, property_value, sqft, year_built, work_type,
                        lead_score, source, import_batch, status, email_status, notes)
                    VALUES (:id, :first_name, :last_name, :full_name, :phone, :phone_2, :email,
                        :address, :city, :state, :zip_code, :property_value, :sqft, :year_built, :work_type,
                        :lead_score, :source, :import_batch, :status, :email_status, :notes)
                    ON CONFLICT (address, city, state) DO NOTHING
                """)
                result = await db.execute(stmt, batch)
                imported += result.rowcount
                skipped += len(batch) - result.rowcount

        await db.commit()
    except FileNotFoundError:
        raise ValidationError(f"CSV file not found at {CSV_PATH}")
    except Exception as e:
        errors += 1
        raise ValidationError(f"Import error: {str(e)}")

    return ImportResult(
        imported=imported,
        skipped=skipped,
        errors=errors,
        total_processed=total,
        batch_id=batch_id,
    )
