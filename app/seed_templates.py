"""Seed 4 starter email templates for Maas Verde."""

TEMPLATES = [
    {
        "name": "Introduction",
        "subject": "Maas Verde Landscape Restoration - Serving {{city}} Homeowners",
        "category": "introduction",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:Georgia,serif;background:#f9fafb;">
<div style="max-width:600px;margin:0 auto;background:#fff;">
  <div style="background:#1a3a2a;padding:30px;text-align:center;">
    <h1 style="color:#4ade80;margin:0;font-size:28px;">Maas Verde</h1>
    <p style="color:#86efac;margin:5px 0 0;font-size:14px;letter-spacing:2px;">LANDSCAPE RESTORATION</p>
  </div>
  <div style="padding:30px;">
    <h2 style="color:#1a3a2a;margin-top:0;">Hello {{first_name}},</h2>
    <p style="color:#374151;line-height:1.7;">We're Maas Verde, Austin's premier landscape restoration company. We specialize in transforming outdoor spaces across the {{city}} area with native Texas plantings, sustainable hardscaping, and erosion control.</p>
    <p style="color:#374151;line-height:1.7;">Whether you're looking to restore your yard after construction, create a drought-resistant landscape, or enhance your property's curb appeal, our team brings decades of expertise to every project.</p>
    <div style="text-align:center;margin:30px 0;">
      <a href="https://maasverde.ecbtx.com" style="background:#16a34a;color:#fff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block;">Explore Our Services</a>
    </div>
    <p style="color:#374151;line-height:1.7;">We'd love to learn about your property and share ideas for how we can help. Reply to this email or give us a call anytime.</p>
    <p style="color:#1a3a2a;font-weight:bold;margin-top:25px;">The Maas Verde Team</p>
  </div>
  <div style="background:#f3f4f6;padding:20px;text-align:center;font-size:12px;color:#9ca3af;">
    <p>Maas Verde Landscape Restoration | Austin, TX</p>
  </div>
</div>
</body>
</html>""",
        "text_body": "Hello {{first_name}},\n\nWe're Maas Verde, Austin's premier landscape restoration company serving the {{city}} area.\n\nWhether you're looking to restore your yard, create a drought-resistant landscape, or enhance curb appeal, we can help.\n\nVisit us: https://maasverde.ecbtx.com\n\nThe Maas Verde Team",
    },
    {
        "name": "Seasonal Promo",
        "subject": "Spring Landscape Special - Transform Your {{city}} Property",
        "category": "promotion",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:Georgia,serif;background:#f9fafb;">
<div style="max-width:600px;margin:0 auto;background:#fff;">
  <div style="background:linear-gradient(135deg,#1a3a2a,#16a34a);padding:40px 30px;text-align:center;">
    <h1 style="color:#fff;margin:0;font-size:32px;">Spring Special</h1>
    <p style="color:#bbf7d0;margin:10px 0 0;font-size:18px;">Save 15% on Landscape Restoration</p>
  </div>
  <div style="padding:30px;">
    <h2 style="color:#1a3a2a;margin-top:0;">Hey {{first_name}},</h2>
    <p style="color:#374151;line-height:1.7;">Spring is the perfect time to invest in your outdoor space. For a limited time, we're offering <strong>15% off</strong> all landscape restoration projects for {{city}} homeowners.</p>
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:20px;margin:20px 0;">
      <h3 style="color:#16a34a;margin-top:0;">Popular Spring Services:</h3>
      <ul style="color:#374151;line-height:2;">
        <li>Native Texas Plant Installation</li>
        <li>Drought-Resistant Landscaping</li>
        <li>Erosion Control & Grading</li>
        <li>Hardscape & Patio Design</li>
        <li>Irrigation System Installation</li>
      </ul>
    </div>
    <div style="text-align:center;margin:30px 0;">
      <a href="https://maasverde.ecbtx.com" style="background:#16a34a;color:#fff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block;">Claim Your 15% Discount</a>
    </div>
    <p style="color:#6b7280;font-size:13px;">Offer valid for projects scheduled by end of season. Cannot be combined with other promotions.</p>
  </div>
  <div style="background:#f3f4f6;padding:20px;text-align:center;font-size:12px;color:#9ca3af;">
    <p>Maas Verde Landscape Restoration | Austin, TX</p>
  </div>
</div>
</body>
</html>""",
        "text_body": "Hey {{first_name}},\n\nSpring is the perfect time to invest in your outdoor space. We're offering 15% off all landscape restoration projects for {{city}} homeowners.\n\nPopular services: Native plantings, drought-resistant landscaping, erosion control, hardscaping, irrigation.\n\nClaim your discount: https://maasverde.ecbtx.com\n\nMaas Verde Team",
    },
    {
        "name": "Follow-Up",
        "subject": "We noticed your property at {{address}}...",
        "category": "follow_up",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:Georgia,serif;background:#f9fafb;">
<div style="max-width:600px;margin:0 auto;background:#fff;">
  <div style="background:#1a3a2a;padding:25px 30px;">
    <h1 style="color:#4ade80;margin:0;font-size:24px;">Maas Verde</h1>
  </div>
  <div style="padding:30px;">
    <h2 style="color:#1a3a2a;margin-top:0;">Hi {{first_name}},</h2>
    <p style="color:#374151;line-height:1.7;">We recently reached out about landscape restoration services in {{city}}, and wanted to follow up.</p>
    <p style="color:#374151;line-height:1.7;">Your property at <strong>{{address}}</strong> could be a great candidate for our services. Many homeowners in your area have transformed their outdoor spaces with our help.</p>
    <div style="background:#fef3c7;border-left:4px solid #f59e0b;padding:15px 20px;margin:20px 0;">
      <p style="color:#92400e;margin:0;font-weight:bold;">Did you know?</p>
      <p style="color:#92400e;margin:5px 0 0;">Professional landscape restoration can increase property value by 15-20%. For a property like yours, that could mean tens of thousands in added value.</p>
    </div>
    <p style="color:#374151;line-height:1.7;">We offer <strong>free on-site consultations</strong> — no obligation, just expert advice on what's possible for your space.</p>
    <div style="text-align:center;margin:30px 0;">
      <a href="https://maasverde.ecbtx.com" style="background:#16a34a;color:#fff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block;">Schedule Free Consultation</a>
    </div>
    <p style="color:#1a3a2a;">Best regards,<br><strong>The Maas Verde Team</strong></p>
  </div>
  <div style="background:#f3f4f6;padding:20px;text-align:center;font-size:12px;color:#9ca3af;">
    <p>Maas Verde Landscape Restoration | Austin, TX</p>
  </div>
</div>
</body>
</html>""",
        "text_body": "Hi {{first_name}},\n\nWe recently reached out about landscape restoration services in {{city}} and wanted to follow up.\n\nYour property at {{address}} could be a great candidate for our services.\n\nDid you know? Professional landscape restoration can increase property value by 15-20%.\n\nWe offer free on-site consultations: https://maasverde.ecbtx.com\n\nThe Maas Verde Team",
    },
    {
        "name": "Re-engagement",
        "subject": "We miss you, {{first_name}} - Special offer inside",
        "category": "re_engagement",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:Georgia,serif;background:#f9fafb;">
<div style="max-width:600px;margin:0 auto;background:#fff;">
  <div style="background:#1a3a2a;padding:25px 30px;">
    <h1 style="color:#4ade80;margin:0;font-size:24px;">Maas Verde</h1>
  </div>
  <div style="padding:30px;">
    <h2 style="color:#1a3a2a;margin-top:0;">Hi {{first_name}},</h2>
    <p style="color:#374151;line-height:1.7;">It's been a while since we connected, and we wanted to check in. We've been busy transforming outdoor spaces across {{city}}, and we'd love to help you too.</p>
    <p style="color:#374151;line-height:1.7;">As a thank-you for your continued interest, we're offering an <strong>exclusive 20% discount</strong> on any landscape restoration project booked this month.</p>
    <div style="background:#f0fdf4;border:2px solid #16a34a;border-radius:8px;padding:25px;margin:25px 0;text-align:center;">
      <p style="color:#16a34a;font-size:24px;font-weight:bold;margin:0;">20% OFF</p>
      <p style="color:#374151;margin:5px 0 0;">Your landscape restoration project</p>
      <p style="color:#6b7280;font-size:13px;margin:10px 0 0;">Use code: COMEBACK20</p>
    </div>
    <p style="color:#374151;line-height:1.7;">Whether it's a complete yard makeover or a targeted improvement, our team is ready to bring your vision to life.</p>
    <div style="text-align:center;margin:30px 0;">
      <a href="https://maasverde.ecbtx.com" style="background:#16a34a;color:#fff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block;">Redeem Your Discount</a>
    </div>
    <p style="color:#1a3a2a;">Warmly,<br><strong>The Maas Verde Team</strong></p>
  </div>
  <div style="background:#f3f4f6;padding:20px;text-align:center;font-size:12px;color:#9ca3af;">
    <p>Maas Verde Landscape Restoration | Austin, TX</p>
  </div>
</div>
</body>
</html>""",
        "text_body": "Hi {{first_name}},\n\nIt's been a while since we connected. We've been transforming outdoor spaces across {{city}}.\n\nExclusive offer: 20% OFF any landscape restoration project this month. Use code: COMEBACK20\n\nBook now: https://maasverde.ecbtx.com\n\nThe Maas Verde Team",
    },
]
