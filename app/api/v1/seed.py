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


@router.post("/seed/mail-templates")
async def seed_mail_templates(db: DbSession):
    """Seed starter direct mail templates (postcards & letters)."""
    from sqlalchemy import select
    from app.models.direct_mail import MailTemplate

    MAIL_TEMPLATES = [
        {
            "name": "Postcard — Spring Intro",
            "mail_type": "postcard",
            "size": "6x4",
            "category": "introduction",
            "description": "Eye-catching spring intro postcard for new prospect outreach",
            "front_html": """<div style="font-family:Arial,sans-serif;padding:24px;background:linear-gradient(135deg,#065f46,#059669);color:white;height:100%;box-sizing:border-box;">
<h1 style="margin:0 0 8px;font-size:22px;">Your Landscape Deserves Better</h1>
<p style="margin:0 0 16px;font-size:13px;opacity:0.9;">Professional restoration &amp; maintenance by Maas Verde</p>
<div style="background:white;color:#065f46;padding:12px 18px;border-radius:8px;display:inline-block;font-weight:bold;font-size:14px;">FREE Consultation — Call Today!</div>
<p style="margin:16px 0 0;font-size:18px;font-weight:bold;">(512) 555-VERDE</p>
</div>""",
            "back_html": """<div style="font-family:Arial,sans-serif;padding:24px;height:100%;box-sizing:border-box;">
<p style="font-size:14px;margin:0 0 8px;"><strong>Dear {{full_name}},</strong></p>
<p style="font-size:12px;margin:0 0 12px;color:#555;">Your property at <strong>{{address}}</strong> in {{city}} could benefit from our expert landscape services.</p>
<ul style="font-size:12px;color:#333;padding-left:18px;margin:0 0 12px;">
<li>Native plant landscaping</li>
<li>Erosion control &amp; grading</li>
<li>Irrigation design</li>
<li>Seasonal maintenance plans</li>
</ul>
<p style="font-size:12px;color:#555;margin:0;">Visit <strong>maasverde.com</strong> or call <strong>(512) 555-VERDE</strong></p>
</div>""",
        },
        {
            "name": "Postcard — Seasonal Promo",
            "mail_type": "postcard",
            "size": "6x9",
            "category": "promotion",
            "description": "Larger seasonal promotion postcard with discount offer",
            "front_html": """<div style="font-family:Arial,sans-serif;padding:32px;background:linear-gradient(135deg,#92400e,#d97706);color:white;height:100%;box-sizing:border-box;">
<h1 style="margin:0 0 12px;font-size:28px;">SPRING SPECIAL</h1>
<div style="font-size:48px;font-weight:900;margin:0 0 8px;">15% OFF</div>
<p style="margin:0 0 16px;font-size:15px;">Landscape restoration &amp; native plant installation</p>
<div style="background:white;color:#92400e;padding:10px 20px;border-radius:8px;display:inline-block;font-weight:bold;">Limited Time — Book by March 31!</div>
</div>""",
            "back_html": """<div style="font-family:Arial,sans-serif;padding:32px;height:100%;box-sizing:border-box;">
<p style="font-size:15px;margin:0 0 10px;"><strong>{{full_name}}</strong></p>
<p style="font-size:13px;margin:0 0 16px;color:#555;">As a {{city}} homeowner, you qualify for our exclusive spring discount on professional landscape services.</p>
<div style="background:#f3f4f6;padding:16px;border-radius:8px;margin:0 0 16px;">
<p style="font-size:13px;margin:0 0 4px;"><strong>Use code: SPRING2026</strong></p>
<p style="font-size:12px;margin:0;color:#666;">Valid for new service agreements. Cannot combine with other offers.</p>
</div>
<p style="font-size:12px;color:#555;margin:0;">Maas Verde Landscape Restoration | (512) 555-VERDE | maasverde.com</p>
</div>""",
        },
        {
            "name": "Letter — Follow Up",
            "mail_type": "letter",
            "size": "8.5x11",
            "category": "follow_up",
            "description": "Full-page letter for follow-up communication with prospects",
            "front_html": """<div style="font-family:Georgia,serif;padding:48px;height:100%;box-sizing:border-box;line-height:1.6;">
<div style="text-align:right;color:#065f46;font-weight:bold;margin-bottom:32px;">
<p style="margin:0;">Maas Verde Landscape Restoration</p>
<p style="margin:0;font-size:12px;color:#666;">Austin, TX | (512) 555-VERDE</p>
</div>
<p style="margin:0 0 24px;">Dear <strong>{{full_name}}</strong>,</p>
<p style="margin:0 0 16px;">We recently reached out about professional landscape services for your property at <strong>{{address}}</strong> in <strong>{{city}}, {{state}} {{zip_code}}</strong>.</p>
<p style="margin:0 0 16px;">As Central Texas's premier landscape restoration company, we specialize in:</p>
<ul style="margin:0 0 16px;padding-left:24px;">
<li>Native &amp; adaptive plant design</li>
<li>Hardscaping &amp; retaining walls</li>
<li>Irrigation system design &amp; repair</li>
<li>Erosion control &amp; land grading</li>
<li>Ongoing seasonal maintenance contracts</li>
</ul>
<p style="margin:0 0 16px;">We'd love to offer you a <strong>free, no-obligation consultation</strong> to assess your property and provide a custom quote.</p>
<p style="margin:0 0 24px;">Simply call us at <strong>(512) 555-VERDE</strong> or visit <strong>maasverde.com</strong> to schedule.</p>
<p style="margin:0;">Warm regards,</p>
<p style="margin:8px 0 0;font-weight:bold;color:#065f46;">The Maas Verde Team</p>
</div>""",
        },
        {
            "name": "Letter — Re-Engagement",
            "mail_type": "letter",
            "size": "8.5x11",
            "category": "re_engagement",
            "description": "Re-engagement letter for prospects who haven't responded",
            "front_html": """<div style="font-family:Georgia,serif;padding:48px;height:100%;box-sizing:border-box;line-height:1.6;">
<div style="text-align:right;color:#065f46;font-weight:bold;margin-bottom:32px;">
<p style="margin:0;">Maas Verde Landscape Restoration</p>
<p style="margin:0;font-size:12px;color:#666;">Austin, TX | (512) 555-VERDE</p>
</div>
<p style="margin:0 0 24px;">Dear <strong>{{full_name}}</strong>,</p>
<p style="margin:0 0 16px;">We haven't heard from you in a while, and we wanted to check in. Your property at <strong>{{address}}</strong> is in one of {{city}}'s most beautiful neighborhoods, and we'd be honored to help you enhance it.</p>
<div style="background:#f0fdf4;border:2px solid #065f46;padding:20px;border-radius:8px;margin:0 0 20px;text-align:center;">
<p style="margin:0 0 8px;font-size:18px;font-weight:bold;color:#065f46;">Special Offer Just For You</p>
<p style="margin:0;font-size:24px;font-weight:900;color:#059669;">$100 OFF</p>
<p style="margin:4px 0 0;font-size:13px;color:#666;">Your first service when you book before the end of the month</p>
</div>
<p style="margin:0 0 16px;">Whether you need a full landscape redesign or seasonal maintenance, our team of experts is ready to transform your outdoor space.</p>
<p style="margin:0 0 24px;">Call <strong>(512) 555-VERDE</strong> or reply to this letter to schedule your free consultation.</p>
<p style="margin:0;">Best regards,</p>
<p style="margin:8px 0 0;font-weight:bold;color:#065f46;">The Maas Verde Team</p>
</div>""",
        },
    ]

    created = 0
    for t in MAIL_TEMPLATES:
        existing = await db.execute(
            select(MailTemplate).where(MailTemplate.name == t["name"])
        )
        if existing.scalars().first():
            continue
        template = MailTemplate(**t)
        db.add(template)
        created += 1

    await db.commit()
    return {"message": f"Seeded {created} mail templates", "created": created}
