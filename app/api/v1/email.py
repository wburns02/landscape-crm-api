from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.exceptions import NotFoundError, ValidationError
from app.models.email_campaign import (
    EmailCampaign,
    EmailCampaignRecipient,
    EmailSend,
    EmailTemplate,
)
from app.models.prospect import Prospect
from app.schemas.email import (
    AIRecommendationResponse,
    AddProspectsRequest,
    AddProspectsResponse,
    CampaignStatsResponse,
    EmailCampaignCreate,
    EmailCampaignResponse,
    EmailCampaignUpdate,
    EmailTemplateCreate,
    EmailTemplateResponse,
    EmailTemplateUpdate,
    SegmentRecommendation,
    SendTestRequest,
    SendTestResponse,
)
from app.services.email_service import render_template, send_email

router = APIRouter(prefix="/email", tags=["email"])


# ---- Templates ----

@router.get("/templates", response_model=list[EmailTemplateResponse])
async def list_templates(db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(EmailTemplate).order_by(EmailTemplate.created_at.desc()))
    return result.scalars().all()


@router.get("/templates/{template_id}", response_model=EmailTemplateResponse)
async def get_template(template_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    template = result.scalars().first()
    if not template:
        raise NotFoundError("EmailTemplate", str(template_id))
    return template


@router.post("/templates", response_model=EmailTemplateResponse, status_code=201)
async def create_template(data: EmailTemplateCreate, db: DbSession, current_user: CurrentUser):
    template = EmailTemplate(**data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.patch("/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_template(template_id: UUID, data: EmailTemplateUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    template = result.scalars().first()
    if not template:
        raise NotFoundError("EmailTemplate", str(template_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/templates/{template_id}")
async def delete_template(template_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    template = result.scalars().first()
    if not template:
        raise NotFoundError("EmailTemplate", str(template_id))
    await db.delete(template)
    await db.commit()
    return {"message": "Template deleted"}


# ---- Campaigns ----

@router.get("/campaigns", response_model=list[EmailCampaignResponse])
async def list_campaigns(db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(EmailCampaign).order_by(EmailCampaign.created_at.desc())
    )
    campaigns = result.scalars().all()
    response = []
    for c in campaigns:
        count_result = await db.execute(
            select(func.count()).select_from(EmailCampaignRecipient)
            .where(EmailCampaignRecipient.campaign_id == c.id)
        )
        recipient_count = count_result.scalar() or 0
        resp = EmailCampaignResponse.model_validate(c)
        resp.recipient_count = recipient_count
        response.append(resp)
    return response


@router.get("/campaigns/ai-recommend", response_model=AIRecommendationResponse)
async def ai_recommend(db: DbSession, current_user: CurrentUser):
    # Count unreached prospects
    unreached = await db.execute(
        select(func.count()).select_from(Prospect)
        .where(Prospect.status == "new")
        .where(Prospect.last_contacted_at.is_(None))
    )
    total_unreached = unreached.scalar() or 0

    # Build segments by city for high-value prospects
    segments = []
    top_cities_result = await db.execute(
        select(Prospect.city, func.count(), func.avg(Prospect.lead_score), func.avg(Prospect.property_value))
        .where(Prospect.status == "new")
        .where(Prospect.last_contacted_at.is_(None))
        .where(Prospect.city.isnot(None))
        .group_by(Prospect.city)
        .order_by(func.count().desc())
        .limit(5)
    )
    for city, count, avg_score, avg_value in top_cities_result.all():
        segments.append(SegmentRecommendation(
            segment_name=f"{city} Homeowners",
            description=f"{count:,} homeowners in {city} who haven't been contacted",
            prospect_count=count,
            avg_lead_score=round(avg_score or 0, 1),
            avg_property_value=round(avg_value or 0, 0),
            suggested_template="Introduction",
        ))

    # High-value segment
    hv_result = await db.execute(
        select(func.count(), func.avg(Prospect.lead_score), func.avg(Prospect.property_value))
        .where(Prospect.status == "new")
        .where(Prospect.last_contacted_at.is_(None))
        .where(Prospect.property_value >= 500000)
    )
    hv_row = hv_result.one_or_none()
    if hv_row and hv_row[0] > 0:
        segments.append(SegmentRecommendation(
            segment_name="High-Value Properties ($500K+)",
            description=f"{hv_row[0]:,} high-value homeowners, never contacted",
            prospect_count=hv_row[0],
            avg_lead_score=round(hv_row[1] or 0, 1),
            avg_property_value=round(hv_row[2] or 0, 0),
            suggested_template="Introduction",
        ))

    # New construction segment
    nc_result = await db.execute(
        select(func.count(), func.avg(Prospect.lead_score), func.avg(Prospect.property_value))
        .where(Prospect.status == "new")
        .where(Prospect.last_contacted_at.is_(None))
        .where(Prospect.work_type == "new_construction")
    )
    nc_row = nc_result.one_or_none()
    if nc_row and nc_row[0] > 0:
        segments.append(SegmentRecommendation(
            segment_name="New Construction Homeowners",
            description=f"{nc_row[0]:,} new construction homeowners — prime for landscape restoration",
            prospect_count=nc_row[0],
            avg_lead_score=round(nc_row[1] or 0, 1),
            avg_property_value=round(nc_row[2] or 0, 0),
            suggested_template="Seasonal Promo",
        ))

    return AIRecommendationResponse(
        segments=segments,
        best_send_times=[
            "Tuesday 9:00 AM - 11:00 AM",
            "Wednesday 10:00 AM - 12:00 PM",
            "Thursday 9:00 AM - 11:00 AM",
        ],
        cadence=[
            "Day 0: Initial introduction email",
            "Day 3: Follow-up with seasonal services",
            "Day 7: Property-specific value proposition",
            "Day 14: Re-engagement with special offer",
        ],
        total_unreached=total_unreached,
    )


@router.get("/campaigns/{campaign_id}", response_model=EmailCampaignResponse)
async def get_campaign(campaign_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(EmailCampaign).where(EmailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("EmailCampaign", str(campaign_id))
    count_result = await db.execute(
        select(func.count()).select_from(EmailCampaignRecipient)
        .where(EmailCampaignRecipient.campaign_id == campaign.id)
    )
    resp = EmailCampaignResponse.model_validate(campaign)
    resp.recipient_count = count_result.scalar() or 0
    return resp


@router.get("/campaigns/{campaign_id}/stats", response_model=CampaignStatsResponse)
async def campaign_stats(campaign_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(EmailCampaign).where(EmailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("EmailCampaign", str(campaign_id))

    total = await db.execute(
        select(func.count()).select_from(EmailCampaignRecipient)
        .where(EmailCampaignRecipient.campaign_id == campaign_id)
    )
    total_recipients = total.scalar() or 0

    sent = campaign.sent_count
    opened = campaign.open_count
    clicked = campaign.click_count
    bounced = campaign.bounce_count

    return CampaignStatsResponse(
        id=campaign.id,
        name=campaign.name,
        status=campaign.status,
        total_recipients=total_recipients,
        sent=sent,
        opened=opened,
        clicked=clicked,
        bounced=bounced,
        open_rate=round(opened / sent * 100, 1) if sent > 0 else 0,
        click_rate=round(clicked / sent * 100, 1) if sent > 0 else 0,
        bounce_rate=round(bounced / sent * 100, 1) if sent > 0 else 0,
    )


@router.post("/campaigns", response_model=EmailCampaignResponse, status_code=201)
async def create_campaign(data: EmailCampaignCreate, db: DbSession, current_user: CurrentUser):
    campaign = EmailCampaign(**data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    resp = EmailCampaignResponse.model_validate(campaign)
    resp.recipient_count = 0
    return resp


@router.patch("/campaigns/{campaign_id}", response_model=EmailCampaignResponse)
async def update_campaign(campaign_id: UUID, data: EmailCampaignUpdate, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(EmailCampaign).where(EmailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("EmailCampaign", str(campaign_id))
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, key, value)
    await db.commit()
    await db.refresh(campaign)
    count_result = await db.execute(
        select(func.count()).select_from(EmailCampaignRecipient)
        .where(EmailCampaignRecipient.campaign_id == campaign.id)
    )
    resp = EmailCampaignResponse.model_validate(campaign)
    resp.recipient_count = count_result.scalar() or 0
    return resp


@router.post("/campaigns/{campaign_id}/add-prospects", response_model=AddProspectsResponse)
async def add_prospects_to_campaign(
    campaign_id: UUID,
    data: AddProspectsRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    result = await db.execute(select(EmailCampaign).where(EmailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("EmailCampaign", str(campaign_id))

    # Build prospect query with filters
    query = select(Prospect.id).where(Prospect.email.isnot(None)).where(Prospect.email != "")
    query = query.where(Prospect.email_status.in_(["unknown", "valid"]))
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

    # Exclude already-added prospects
    existing = select(EmailCampaignRecipient.prospect_id).where(
        EmailCampaignRecipient.campaign_id == campaign_id
    )
    query = query.where(Prospect.id.notin_(existing))

    if data.limit:
        query = query.limit(data.limit)

    prospect_ids = await db.execute(query)
    ids = [r[0] for r in prospect_ids.all()]

    added = 0
    for pid in ids:
        recipient = EmailCampaignRecipient(
            campaign_id=campaign_id,
            prospect_id=pid,
        )
        db.add(recipient)
        added += 1

    await db.commit()
    return AddProspectsResponse(added=added, campaign_id=campaign_id)


@router.post("/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(EmailCampaign)
        .options(selectinload(EmailCampaign.template))
        .where(EmailCampaign.id == campaign_id)
    )
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("EmailCampaign", str(campaign_id))
    if not campaign.template:
        raise ValidationError("Campaign has no template assigned")

    campaign.status = "sending"
    await db.commit()

    # Get pending recipients with emails
    recipients_result = await db.execute(
        select(EmailCampaignRecipient)
        .options(selectinload(EmailCampaignRecipient.prospect))
        .where(EmailCampaignRecipient.campaign_id == campaign_id)
        .where(EmailCampaignRecipient.status == "pending")
        .limit(50)
    )
    recipients = recipients_result.scalars().all()

    sent = 0
    for r in recipients:
        if not r.prospect or not r.prospect.email:
            r.status = "bounced"
            continue

        variables = {
            "first_name": r.prospect.first_name,
            "last_name": r.prospect.last_name,
            "city": r.prospect.city or "Austin",
            "address": r.prospect.address,
            "work_type": r.prospect.work_type or "home improvement",
            "company_name": "Maas Verde Landscape Restoration",
        }
        html = render_template(campaign.template.html_body, variables)
        subject = render_template(campaign.template.subject, variables)

        email_result = await send_email(
            to=r.prospect.email,
            subject=subject,
            html=html,
            text=campaign.template.text_body,
            prospect_id=str(r.prospect.id),
        )

        if email_result.get("id"):
            r.status = "sent"
            from datetime import datetime, timezone
            r.sent_at = datetime.now(timezone.utc)
            sent += 1

            send_record = EmailSend(
                prospect_id=r.prospect.id,
                campaign_id=campaign_id,
                template_id=campaign.template_id,
                to_email=r.prospect.email,
                subject=subject,
                status="sent",
                resend_message_id=email_result["id"],
            )
            db.add(send_record)
        else:
            r.status = "bounced"
            campaign.bounce_count += 1

    campaign.sent_count += sent
    # Check if all done
    pending_count = await db.execute(
        select(func.count()).select_from(EmailCampaignRecipient)
        .where(EmailCampaignRecipient.campaign_id == campaign_id)
        .where(EmailCampaignRecipient.status == "pending")
    )
    if (pending_count.scalar() or 0) == 0:
        campaign.status = "sent"

    await db.commit()
    return {"message": f"Sent {sent} emails", "sent": sent, "status": campaign.status}


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: UUID, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(EmailCampaign).where(EmailCampaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise NotFoundError("EmailCampaign", str(campaign_id))
    campaign.status = "paused"
    await db.commit()
    return {"message": "Campaign paused"}


@router.post("/send-test", response_model=SendTestResponse)
async def send_test_email(data: SendTestRequest, db: DbSession, current_user: CurrentUser):
    subject = data.subject or "Test Email from Maas Verde"
    html = data.html_body or "<h1>Test Email</h1><p>This is a test email from Maas Verde CRM.</p>"

    if data.template_id:
        result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == data.template_id))
        template = result.scalars().first()
        if template:
            subject = template.subject
            html = template.html_body

    email_result = await send_email(to=data.to_email, subject=subject, html=html)

    if email_result.get("id"):
        return SendTestResponse(success=True, message="Test email sent", resend_id=email_result["id"])
    else:
        return SendTestResponse(
            success=False,
            message=email_result.get("error", "Failed to send"),
            resend_id=None,
        )


@router.post("/webhooks/resend")
async def resend_webhook(payload: dict):
    event_type = payload.get("type", "")
    data = payload.get("data", {})
    email_id = data.get("email_id", "")

    if not email_id:
        return {"status": "ignored"}

    # This would update EmailSend records based on resend events
    # For now, just acknowledge
    return {"status": "received", "type": event_type}
