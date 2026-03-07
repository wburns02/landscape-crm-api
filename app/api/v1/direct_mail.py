import csv
import io
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.direct_mail import DirectMailCampaign, DirectMailRecipient, MailTemplate
from app.models.prospect import Prospect
from app.schemas.direct_mail import (
    AddMailRecipientsRequest,
    AddMailRecipientsResponse,
    DirectMailCampaignCreate,
    DirectMailCampaignResponse,
    DirectMailCampaignUpdate,
    MailTemplateCreate,
    MailTemplateResponse,
    MailTemplateUpdate,
)

router = APIRouter(prefix="/direct-mail", tags=["direct-mail"])

# Cost estimates per piece (industry averages)
COST_ESTIMATES = {
    "postcard_6x4": 0.45,
    "postcard_6x9": 0.65,
    "letter_8.5x11": 0.85,
}


# ---- Mail Templates ----

@router.get("/templates", response_model=list[MailTemplateResponse])
async def list_mail_templates(db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(MailTemplate).order_by(MailTemplate.created_at.desc()))
    return result.scalars().all()


@router.post("/templates", response_model=MailTemplateResponse, status_code=201)
async def create_mail_template(data: MailTemplateCreate, db: DbSession, current_user: CurrentUser):
    template = MailTemplate(**data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.patch("/templates/{template_id}", response_model=MailTemplateResponse)
async def update_mail_template(template_id: UUID, data: MailTemplateUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(MailTemplate).where(MailTemplate.id == template_id))
    template = result.scalars().first()
    if not template:
        raise NotFoundError("MailTemplate", str(template_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/templates/{template_id}")
async def delete_mail_template(template_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(MailTemplate).where(MailTemplate.id == template_id))
    template = result.scalars().first()
    if not template:
        raise NotFoundError("MailTemplate", str(template_id))
    await db.delete(template)
    await db.commit()
    return {"message": "Template deleted"}


# ---- Campaigns ----

@router.get("/campaigns", response_model=list[DirectMailCampaignResponse])
async def list_campaigns(db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(DirectMailCampaign).order_by(DirectMailCampaign.created_at.desc()))
    campaigns = result.scalars().all()
    response = []
    for c in campaigns:
        count_result = await db.execute(
            select(func.count()).select_from(DirectMailRecipient)
            .where(DirectMailRecipient.campaign_id == c.id)
        )
        resp = DirectMailCampaignResponse.model_validate(c)
        resp.recipient_count = count_result.scalar() or 0
        response.append(resp)
    return response


@router.post("/campaigns", response_model=DirectMailCampaignResponse, status_code=201)
async def create_campaign(data: DirectMailCampaignCreate, db: DbSession, current_user: CurrentUser):
    campaign = DirectMailCampaign(**data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    resp = DirectMailCampaignResponse.model_validate(campaign)
    resp.recipient_count = 0
    return resp


@router.get("/campaigns/{campaign_id}", response_model=DirectMailCampaignResponse)
async def get_campaign(campaign_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(DirectMailCampaign).where(DirectMailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("DirectMailCampaign", str(campaign_id))
    count_result = await db.execute(
        select(func.count()).select_from(DirectMailRecipient)
        .where(DirectMailRecipient.campaign_id == campaign.id)
    )
    resp = DirectMailCampaignResponse.model_validate(campaign)
    resp.recipient_count = count_result.scalar() or 0
    return resp


@router.patch("/campaigns/{campaign_id}", response_model=DirectMailCampaignResponse)
async def update_campaign(campaign_id: UUID, data: DirectMailCampaignUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(DirectMailCampaign).where(DirectMailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("DirectMailCampaign", str(campaign_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, key, value)
    # Update timestamps based on status transitions
    if data.status == "sent_to_printer" and not campaign.sent_to_printer_at:
        campaign.sent_to_printer_at = datetime.now(timezone.utc)
    elif data.status == "mailed" and not campaign.mailed_at:
        campaign.mailed_at = datetime.now(timezone.utc)
    elif data.status == "delivered" and not campaign.delivered_at:
        campaign.delivered_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(campaign)
    count_result = await db.execute(
        select(func.count()).select_from(DirectMailRecipient)
        .where(DirectMailRecipient.campaign_id == campaign.id)
    )
    resp = DirectMailCampaignResponse.model_validate(campaign)
    resp.recipient_count = count_result.scalar() or 0
    return resp


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(DirectMailCampaign).where(DirectMailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("DirectMailCampaign", str(campaign_id))
    # Delete recipients first
    await db.execute(
        DirectMailRecipient.__table__.delete().where(DirectMailRecipient.campaign_id == campaign_id)
    )
    await db.delete(campaign)
    await db.commit()
    return {"message": "Campaign deleted"}


# ---- Recipients ----

@router.post("/campaigns/{campaign_id}/add-recipients", response_model=AddMailRecipientsResponse)
async def add_recipients(
    campaign_id: UUID,
    data: AddMailRecipientsRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    result = await db.execute(select(DirectMailCampaign).where(DirectMailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("DirectMailCampaign", str(campaign_id))

    # Build prospect query — requires address for physical mail
    query = select(Prospect).where(Prospect.address.isnot(None)).where(Prospect.address != "")
    if data.city:
        query = query.where(Prospect.city.ilike(data.city))
    if data.work_type:
        query = query.where(Prospect.work_type == data.work_type)
    if data.min_score is not None:
        query = query.where(Prospect.lead_score >= data.min_score)
    if data.max_score is not None:
        query = query.where(Prospect.lead_score <= data.max_score)
    if data.min_property_value is not None:
        query = query.where(Prospect.property_value >= data.min_property_value)
    if data.max_property_value is not None:
        query = query.where(Prospect.property_value <= data.max_property_value)

    # Exclude already-added
    existing = select(DirectMailRecipient.prospect_id).where(
        DirectMailRecipient.campaign_id == campaign_id
    )
    query = query.where(Prospect.id.notin_(existing))

    if data.limit:
        query = query.limit(data.limit)

    prospects_result = await db.execute(query)
    prospects = prospects_result.scalars().all()

    added = 0
    for p in prospects:
        recipient = DirectMailRecipient(
            campaign_id=campaign_id,
            prospect_id=p.id,
            full_name=p.full_name or f"{p.first_name} {p.last_name}".strip(),
            address=p.address,
            city=p.city or "Austin",
            state=p.state or "TX",
            zip_code=p.zip_code,
        )
        db.add(recipient)
        added += 1

    # Update estimated cost
    total_recipients = added
    count_result = await db.execute(
        select(func.count()).select_from(DirectMailRecipient)
        .where(DirectMailRecipient.campaign_id == campaign_id)
    )
    total_recipients = (count_result.scalar() or 0) + added
    # Determine size from template if linked (avoid lazy load in async)
    template_size = '6x4'
    if campaign.template_id:
        tmpl_result = await db.execute(select(MailTemplate).where(MailTemplate.id == campaign.template_id))
        tmpl = tmpl_result.scalars().first()
        if tmpl:
            template_size = tmpl.size
    cost_key = f"{campaign.mail_type}_{template_size}"
    per_piece = campaign.cost_per_piece or COST_ESTIMATES.get(cost_key, 0.50)
    campaign.recipient_count = total_recipients
    campaign.estimated_cost = round(total_recipients * per_piece, 2)
    campaign.cost_per_piece = per_piece

    await db.commit()
    return AddMailRecipientsResponse(added=added, campaign_id=str(campaign_id))


@router.get("/campaigns/{campaign_id}/recipients")
async def list_recipients(
    campaign_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    result = await db.execute(select(DirectMailCampaign).where(DirectMailCampaign.id == campaign_id))
    if not result.scalars().first():
        raise NotFoundError("DirectMailCampaign", str(campaign_id))

    count_result = await db.execute(
        select(func.count()).select_from(DirectMailRecipient)
        .where(DirectMailRecipient.campaign_id == campaign_id)
    )
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    recipients_result = await db.execute(
        select(DirectMailRecipient)
        .where(DirectMailRecipient.campaign_id == campaign_id)
        .offset(offset).limit(page_size)
    )
    recipients = recipients_result.scalars().all()

    return {
        "items": [
            {
                "id": str(r.id),
                "full_name": r.full_name,
                "address": r.address,
                "city": r.city,
                "state": r.state,
                "zip_code": r.zip_code,
                "status": r.status,
            }
            for r in recipients
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ---- Export ----

@router.get("/campaigns/{campaign_id}/export")
async def export_campaign_csv(campaign_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(DirectMailCampaign).where(DirectMailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("DirectMailCampaign", str(campaign_id))

    recipients_result = await db.execute(
        select(DirectMailRecipient)
        .where(DirectMailRecipient.campaign_id == campaign_id)
        .where(DirectMailRecipient.status.in_(["pending", "included"]))
    )
    recipients = recipients_result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Full Name", "Address", "City", "State", "Zip Code"])
    for r in recipients:
        writer.writerow([r.full_name, r.address, r.city, r.state, r.zip_code or ""])

    output.seek(0)
    filename = f"mailverde_{campaign.name.replace(' ', '_').lower()}_{len(recipients)}_recipients.csv"

    # Also mark campaign as ready
    if campaign.status == "draft":
        campaign.status = "ready"
        campaign.recipient_count = len(recipients)
        await db.commit()

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/campaigns/{campaign_id}/update-status")
async def update_campaign_status(
    campaign_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    status: str = Query(...),
):
    valid_statuses = ["draft", "ready", "sent_to_printer", "printed", "mailed", "delivered"]
    if status not in valid_statuses:
        raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    result = await db.execute(select(DirectMailCampaign).where(DirectMailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("DirectMailCampaign", str(campaign_id))

    campaign.status = status
    if status == "sent_to_printer" and not campaign.sent_to_printer_at:
        campaign.sent_to_printer_at = datetime.now(timezone.utc)
    elif status == "mailed" and not campaign.mailed_at:
        campaign.mailed_at = datetime.now(timezone.utc)
    elif status == "delivered" and not campaign.delivered_at:
        campaign.delivered_at = datetime.now(timezone.utc)

    await db.commit()
    return {"message": f"Campaign status updated to {status}"}
