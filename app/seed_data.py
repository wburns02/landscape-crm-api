import uuid
from datetime import date, datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract
from app.models.crew import Crew, CrewMember
from app.models.customer import Customer
from app.models.equipment import Equipment
from app.models.inventory_item import InventoryItem
from app.models.invoice import Invoice
from app.models.job import Job
from app.models.lead import Lead
from app.models.payment import Payment
from app.models.photo import Photo
from app.models.quote import Quote
from app.models.schedule_event import ScheduleEvent
from app.models.settings import SystemSettings
from app.models.time_entry import TimeEntry
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
today = date.today()


async def seed(db: AsyncSession):
    """Create realistic demo data for GreenScape Landscaping CRM."""

    # ── Users ──────────────────────────────────────────────────────────
    admin = User(
        id=uuid.uuid4(),
        email="admin@greenscape.com",
        password_hash=pwd_context.hash("GreenAdmin123!"),
        full_name="Marcus Green",
        role="admin",
        phone="(512) 555-0101",
        is_active=True,
    )
    crew_lead = User(
        id=uuid.uuid4(),
        email="javier@greenscape.com",
        password_hash=pwd_context.hash("CrewLead123!"),
        full_name="Javier Morales",
        role="crew_lead",
        phone="(512) 555-0102",
        is_active=True,
    )
    tech1 = User(
        id=uuid.uuid4(),
        email="tyler@greenscape.com",
        password_hash=pwd_context.hash("Tech123!"),
        full_name="Tyler Brooks",
        role="technician",
        phone="(512) 555-0103",
    )
    tech2 = User(
        id=uuid.uuid4(),
        email="maria@greenscape.com",
        password_hash=pwd_context.hash("Tech123!"),
        full_name="Maria Santos",
        role="technician",
        phone="(512) 555-0104",
    )
    tech3 = User(
        id=uuid.uuid4(),
        email="david@greenscape.com",
        password_hash=pwd_context.hash("Tech123!"),
        full_name="David Chen",
        role="technician",
        phone="(512) 555-0105",
    )
    users = [admin, crew_lead, tech1, tech2, tech3]
    db.add_all(users)

    # ── Customers ──────────────────────────────────────────────────────
    customers_data = [
        ("Robert", "Thompson", None, "residential", "robert.t@email.com", "(512) 555-1001", "4521 Magnolia Creek Dr", "Austin", "TX", "78745", 30.2100, -97.7800, 12000, "Large corner lot, Bermuda grass", ["premium", "irrigation"], "referral"),
        ("Sarah", "Mitchell", None, "residential", "sarah.m@email.com", "(512) 555-1002", "8903 Live Oak Bend", "Austin", "TX", "78749", 30.2200, -97.8200, 8500, "Shade garden, needs regular mulching", ["organic"], "website"),
        ("James", "Patterson", None, "residential", "james.p@email.com", "(512) 555-1003", "2210 Pecan Valley Rd", "Round Rock", "TX", "78664", 30.5100, -97.6700, 15000, "Pool area needs weekly maintenance", ["pool-area"], "google_ads"),
        ("Lisa", "Hernandez", None, "residential", "lisa.h@email.com", "(512) 555-1004", "7741 Bluebonnet Trail", "Cedar Park", "TX", "78613", 30.5200, -97.8200, 6000, "Xeriscaping front yard, turf backyard", ["xeriscape"], "referral"),
        ("Michael", "Davis", "Davis Property Group", "property_manager", "mdavis@davisprop.com", "(512) 555-1005", "1100 S Congress Ave Ste 300", "Austin", "TX", "78704", 30.2500, -97.7500, None, "Manages 12 residential properties", ["commercial", "multi-property"], "website"),
        ("Karen", "Wilson", None, "residential", "karen.w@email.com", "(512) 555-1006", "5560 Barton Skyway", "Austin", "TX", "78735", 30.2600, -97.8000, 20000, "Estate property, extensive gardens", ["premium", "estate"], "referral"),
        ("Daniel", "Lee", None, "residential", "daniel.l@email.com", "(512) 555-1007", "3324 Settlers Park Dr", "Pflugerville", "TX", "78660", 30.4400, -97.6200, 7500, "New construction, needs full landscaping", ["new-build"], "google_ads"),
        ("Jennifer", "Clark", "Sunrise HOA", "hoa", "jclark@sunrisehoa.org", "(512) 555-1008", "9200 Sunrise Blvd", "Austin", "TX", "78748", 30.1800, -97.8100, None, "HOA common areas, 45 homes", ["hoa", "commercial"], "referral"),
        ("Chris", "Rodriguez", "Hill Country Mall", "commercial", "crodriguez@hcmall.com", "(512) 555-1009", "14000 N IH-35", "Austin", "TX", "78753", 30.3900, -97.6700, None, "Parking lot islands, entrance landscaping", ["commercial", "high-traffic"], "website"),
        ("Amanda", "Foster", None, "residential", "amanda.f@email.com", "(512) 555-1010", "6612 Lost Creek Blvd", "Austin", "TX", "78746", 30.2800, -97.8200, 35000, "Luxury home, extensive tree cover, koi pond", ["luxury", "water-feature"], "referral"),
        ("Brian", "Taylor", "Taylor Ranch", "residential", "brian.t@email.com", "(512) 555-1011", "18500 Hamilton Pool Rd", "Dripping Springs", "TX", "78620", 30.3300, -98.0700, 50000, "Ranch property, native grasses", ["ranch", "native"], "door_hanger"),
        ("Nicole", "Martinez", None, "residential", "nicole.m@email.com", "(512) 555-1012", "4420 Teravista Club Dr", "Round Rock", "TX", "78665", 30.5600, -97.6500, 9000, "HOA-maintained front, backyard is ours", ["standard"], "social_media"),
        ("Steven", "Wang", "Capitol Office Park", "commercial", "swang@capitolop.com", "(512) 555-1013", "8500 Shoal Creek Blvd", "Austin", "TX", "78757", 30.3500, -97.7400, None, "Office complex, 3 buildings, courtyard", ["commercial", "irrigation"], "website"),
        ("Rachel", "Brown", None, "residential", "rachel.b@email.com", "(512) 555-1014", "1905 Westlake Dr", "Austin", "TX", "78746", 30.3100, -97.8000, 18000, "Hillside property, erosion control needed", ["hillside", "premium"], "google_ads"),
        ("Tom", "Garcia", None, "residential", "tom.g@email.com", "(512) 555-1015", "3701 Manchaca Rd", "Austin", "TX", "78704", 30.2300, -97.7800, 5500, "Small urban lot, pollinator garden", ["organic", "pollinator"], "social_media"),
    ]

    customers = []
    spent_values = [4250, 1800, 6500, 2200, 18500, 12000, 3500, 24000, 15000, 8700, 5200, 1950, 11000, 4800, 950]
    job_counts = [12, 6, 18, 8, 52, 24, 4, 48, 36, 15, 10, 5, 28, 9, 3]

    for i, cd in enumerate(customers_data):
        c = Customer(
            id=uuid.uuid4(),
            first_name=cd[0], last_name=cd[1], company_name=cd[2],
            customer_type=cd[3], email=cd[4], phone=cd[5],
            address=cd[6], city=cd[7], state=cd[8], zip_code=cd[9],
            lat=cd[10], lng=cd[11], property_size_sqft=cd[12],
            notes=cd[13], tags=cd[14], source=cd[15],
            total_spent=spent_values[i], job_count=job_counts[i],
        )
        customers.append(c)
    db.add_all(customers)

    # ── Crews ──────────────────────────────────────────────────────────
    crew_a = Crew(id=uuid.uuid4(), name="Alpha Crew", leader_id=crew_lead.id, color="#22c55e", is_active=True)
    crew_b = Crew(id=uuid.uuid4(), name="Bravo Crew", leader_id=tech1.id, color="#3b82f6", is_active=True)
    crew_c = Crew(id=uuid.uuid4(), name="Charlie Crew", leader_id=tech3.id, color="#f59e0b", is_active=True)
    crews = [crew_a, crew_b, crew_c]
    db.add_all(crews)
    await db.flush()

    # Crew members
    members = [
        CrewMember(crew_id=crew_a.id, user_id=crew_lead.id, role="leader"),
        CrewMember(crew_id=crew_a.id, user_id=tech2.id, role="member"),
        CrewMember(crew_id=crew_b.id, user_id=tech1.id, role="leader"),
        CrewMember(crew_id=crew_c.id, user_id=tech3.id, role="leader"),
    ]
    db.add_all(members)

    # ── Jobs ───────────────────────────────────────────────────────────
    job_templates = [
        ("Weekly Mowing & Edging", "maintenance", "lawn_care", "completed", "normal", 1.5, 1.5),
        ("Spring Mulch Installation", "installation", "planting", "completed", "normal", 4.0, 4.5),
        ("Irrigation System Repair", "maintenance", "irrigation", "completed", "high", 2.0, 2.5),
        ("Tree Trimming - Red Oaks", "maintenance", "tree_care", "completed", "normal", 3.0, 3.0),
        ("Fall Leaf Cleanup", "cleanup", "cleanup", "completed", "normal", 3.0, 2.5),
        ("New Flowerbed Installation", "installation", "planting", "in_progress", "normal", 5.0, None),
        ("Hardscape Patio Extension", "installation", "hardscaping", "scheduled", "high", 8.0, None),
        ("Weekly Mowing - Commercial", "maintenance", "lawn_care", "scheduled", "normal", 3.0, None),
        ("Irrigation Winterization", "maintenance", "irrigation", "pending", "normal", 1.5, None),
        ("Stump Grinding", "maintenance", "tree_care", "completed", "low", 2.0, 2.0),
        ("Fence Line Cleanup", "cleanup", "cleanup", "completed", "normal", 2.5, 3.0),
        ("Sod Installation - Backyard", "installation", "lawn_care", "in_progress", "high", 6.0, None),
        ("Monthly Bed Maintenance", "maintenance", "planting", "scheduled", "normal", 2.0, None),
        ("Drainage Solution Install", "installation", "irrigation", "pending", "urgent", 4.0, None),
        ("HOA Common Area Mowing", "maintenance", "lawn_care", "completed", "normal", 4.0, 4.0),
        ("Landscape Design - Front Yard", "installation", "planting", "scheduled", "normal", 6.0, None),
        ("Pruning & Shaping Hedges", "maintenance", "tree_care", "completed", "normal", 2.0, 1.5),
        ("Chemical Weed Treatment", "maintenance", "lawn_care", "completed", "normal", 1.0, 1.0),
        ("Retaining Wall Construction", "installation", "hardscaping", "in_progress", "high", 16.0, None),
        ("Emergency Storm Cleanup", "cleanup", "cleanup", "completed", "urgent", 5.0, 6.0),
        ("Sprinkler Head Replacement", "maintenance", "irrigation", "completed", "normal", 1.0, 1.0),
        ("Seasonal Color Planting", "installation", "planting", "scheduled", "normal", 3.0, None),
        ("Lawn Aeration & Overseeding", "maintenance", "lawn_care", "pending", "normal", 3.0, None),
        ("Outdoor Lighting Install", "installation", "hardscaping", "pending", "low", 4.0, None),
        ("Weekly Maintenance Visit", "maintenance", "lawn_care", "completed", "normal", 1.5, 1.5),
    ]

    jobs = []
    for i, jt in enumerate(job_templates):
        sched_date = today - timedelta(days=30 - i * 2) if i < 12 else today + timedelta(days=(i - 11) * 3)
        customer_idx = i % len(customers)
        crew_idx = i % len(crews)
        j = Job(
            id=uuid.uuid4(),
            customer_id=customers[customer_idx].id,
            title=jt[0],
            description=f"Scheduled {jt[0].lower()} service for {customers[customer_idx].first_name} {customers[customer_idx].last_name}",
            job_type=jt[2],
            status=jt[3],
            priority=jt[4],
            scheduled_date=sched_date.isoformat(),
            scheduled_time="08:00" if i % 3 == 0 else "10:00" if i % 3 == 1 else "13:00",
            estimated_duration_hours=jt[5],
            actual_duration_hours=jt[6],
            crew_id=crews[crew_idx].id,
            address=customers[customer_idx].address,
            lat=customers[customer_idx].lat,
            lng=customers[customer_idx].lng,
            materials_used=[{"item": "Mulch", "quantity": 5, "unit": "yards"}] if "mulch" in jt[0].lower() else [],
            is_recurring=jt[1] == "maintenance",
        )
        jobs.append(j)
    db.add_all(jobs)

    # ── Inventory Items ────────────────────────────────────────────────
    inventory_data = [
        ("Bermuda Sod (pallet)", "plants", "SOD-BER-001", "Premium Bermuda 419 sod, 450 sqft per pallet", "each", 45, 10, 125.00, 225.00, "Austin Sod Farm", "Nursery Yard A"),
        ("St. Augustine Sod (pallet)", "plants", "SOD-STA-001", "Floratam St. Augustine, 450 sqft per pallet", "each", 32, 8, 140.00, 250.00, "Austin Sod Farm", "Nursery Yard A"),
        ("Hardwood Mulch", "mulch", "MUL-HWD-001", "Double-ground hardwood mulch", "yard", 120, 30, 28.00, 65.00, "Central TX Mulch Co", "Bulk Yard B"),
        ("Cedar Mulch", "mulch", "MUL-CED-001", "Aromatic cedar mulch, natural pest deterrent", "yard", 85, 20, 35.00, 75.00, "Central TX Mulch Co", "Bulk Yard B"),
        ("Black Dyed Mulch", "mulch", "MUL-BLK-001", "Premium black-dyed hardwood mulch", "yard", 60, 15, 38.00, 85.00, "Central TX Mulch Co", "Bulk Yard B"),
        ("Scott's Turf Builder", "fertilizer", "FRT-SCT-001", "32-0-4 lawn fertilizer, 15,000 sqft bag", "bag", 48, 12, 32.00, 55.00, "SiteOne Landscape Supply", "Warehouse C"),
        ("Milorganite Organic", "fertilizer", "FRT-MIL-001", "6-4-0 organic nitrogen fertilizer, 32 lb bag", "bag", 36, 10, 14.00, 28.00, "SiteOne Landscape Supply", "Warehouse C"),
        ("Pre-Emergent Herbicide", "chemical", "CHM-PRE-001", "Barricade 65 WDG pre-emergent, 5 lb jug", "each", 18, 5, 85.00, 145.00, "BWI Companies", "Chemical Storage"),
        ("Roundup Pro Max", "chemical", "CHM-RUP-001", "Non-selective herbicide, 2.5 gal", "gallon", 12, 4, 65.00, 110.00, "BWI Companies", "Chemical Storage"),
        ("Mexican White Eagle Flagstone", "hardscape", "HRD-FLG-001", "Natural flagstone, irregular shapes", "ton", 8, 2, 280.00, 485.00, "Austin Stone Depot", "Hardscape Yard D"),
        ("Decomposed Granite", "hardscape", "HRD-DGR-001", "Gold decomposed granite, pathway grade", "ton", 15, 4, 45.00, 95.00, "Austin Stone Depot", "Hardscape Yard D"),
        ("4\" PVC Drain Pipe (10ft)", "hardscape", "HRD-PVC-001", "Corrugated drainage pipe", "each", 40, 10, 8.50, 18.00, "HD Supply", "Warehouse C"),
        ("Red Yucca (1 gal)", "plants", "PLT-RYC-001", "Hesperaloe parviflora, native Texas perennial", "each", 65, 15, 8.00, 18.00, "Barton Springs Nursery", "Nursery Yard A"),
        ("Texas Sage (5 gal)", "shrubs", "SHB-TXS-001", "Leucophyllum frutescens, drought tolerant", "each", 28, 8, 22.00, 45.00, "Barton Springs Nursery", "Nursery Yard A"),
        ("Live Oak (15 gal)", "trees", "TRE-LOK-001", "Quercus virginiana, container grown", "each", 12, 3, 85.00, 195.00, "TreeTown USA", "Nursery Yard A"),
        ("Mexican Sycamore (30 gal)", "trees", "TRE-MSY-001", "Platanus mexicana, fast growing shade tree", "each", 6, 2, 165.00, 350.00, "TreeTown USA", "Nursery Yard A"),
        ("Bermuda Seed (50 lb)", "seed", "SED-BER-001", "Bermuda Common hulled seed blend", "bag", 15, 5, 95.00, 165.00, "SiteOne Landscape Supply", "Warehouse C"),
        ("Zoysia Plugs (tray of 72)", "plants", "PLT-ZOY-001", "Palisades zoysia grass plugs", "flat", 20, 5, 32.00, 65.00, "Austin Sod Farm", "Nursery Yard A"),
        ("Drip Irrigation Kit", "tool", "TUL-DRP-001", "250ft drip line with emitters and fittings", "each", 8, 3, 45.00, 95.00, "Rain Bird", "Warehouse C"),
        ("Landscape Fabric (300ft)", "other", "OTH-FAB-001", "Commercial grade weed barrier, 4ft wide", "each", 22, 6, 35.00, 75.00, "HD Supply", "Warehouse C"),
        ("Expanded Shale", "soil", "SOL-SHL-001", "Soil amendment for clay soils, improves drainage", "yard", 30, 8, 42.00, 85.00, "TXI Operations", "Bulk Yard B"),
        ("Compost Blend", "soil", "SOL-CMP-001", "Dillo Dirt compost, premium organic blend", "yard", 55, 15, 30.00, 62.00, "Austin Resource Recovery", "Bulk Yard B"),
        ("Landscape Boulders", "hardscape", "HRD-BLD-001", "Texas limestone boulders, 12-24 inch", "each", 35, 8, 25.00, 65.00, "Austin Stone Depot", "Hardscape Yard D"),
        ("Mexican Feathergrass (1 gal)", "plants", "PLT-MFG-001", "Nassella tenuissima, ornamental grass", "each", 80, 20, 6.50, 14.00, "Barton Springs Nursery", "Nursery Yard A"),
        ("Hunter PGP Rotor", "tool", "TUL-RTR-001", "Adjustable arc rotor sprinkler head", "each", 50, 15, 18.00, 38.00, "SiteOne Landscape Supply", "Warehouse C"),
        ("Rainbird ESP-TM2 Controller", "tool", "TUL-CTR-001", "12-station WiFi irrigation controller", "each", 5, 2, 165.00, 295.00, "Rain Bird", "Warehouse C"),
        ("Organic Ant Killer", "chemical", "CHM-ANT-001", "Fire ant bait, 25 lb bag", "bag", 14, 4, 28.00, 55.00, "BWI Companies", "Chemical Storage"),
        ("River Rock (1-3 inch)", "hardscape", "HRD-RVR-001", "Polished river rock, decorative ground cover", "ton", 10, 3, 120.00, 225.00, "Austin Stone Depot", "Hardscape Yard D"),
        ("Pink Muhly Grass (1 gal)", "plants", "PLT-PMG-001", "Muhlenbergia capillaris, fall blooming ornamental", "each", 55, 12, 7.50, 16.00, "Barton Springs Nursery", "Nursery Yard A"),
        ("Stihl Trimmer Line (.095)", "tool", "TUL-TRL-001", "Commercial grade trimmer line, 3 lb spool", "each", 25, 8, 22.00, 42.00, "Stihl Dealer", "Warehouse C"),
    ]

    inventory_items = []
    for inv in inventory_data:
        item = InventoryItem(
            id=uuid.uuid4(), name=inv[0], category=inv[1], sku=inv[2],
            description=inv[3], unit=inv[4], quantity_on_hand=inv[5],
            reorder_level=inv[6], unit_cost=inv[7], unit_price=inv[8],
            supplier_name=inv[9], location=inv[11],
        )
        inventory_items.append(item)
    db.add_all(inventory_items)

    # ── Quotes ─────────────────────────────────────────────────────────
    quotes = [
        Quote(id=uuid.uuid4(), customer_id=customers[6].id, quote_number="Q-1001", title="Full Landscape Design & Install",
              status="sent", line_items=[
                  {"description": "Landscape design consultation", "quantity": 1, "unit_price": 200, "total": 200},
                  {"description": "Texas Sage (5 gal) x 12", "quantity": 12, "unit_price": 45, "total": 540},
                  {"description": "Red Yucca (1 gal) x 25", "quantity": 25, "unit_price": 18, "total": 450},
                  {"description": "Hardwood Mulch (yards)", "quantity": 8, "unit_price": 65, "total": 520},
                  {"description": "Installation Labor (hours)", "quantity": 16, "unit_price": 75, "total": 1200},
              ], subtotal=2910, tax_rate=8.25, tax_amount=240.08, total=3150.08,
              valid_until=(today + timedelta(days=30)).isoformat(),
              sent_at=datetime.now(timezone.utc) - timedelta(days=5)),
        Quote(id=uuid.uuid4(), customer_id=customers[13].id, quote_number="Q-1002", title="Hillside Erosion Control",
              status="accepted", line_items=[
                  {"description": "Retaining wall materials", "quantity": 1, "unit_price": 3500, "total": 3500},
                  {"description": "Drainage pipe & fittings", "quantity": 1, "unit_price": 450, "total": 450},
                  {"description": "Native plantings", "quantity": 1, "unit_price": 800, "total": 800},
                  {"description": "Labor (hours)", "quantity": 24, "unit_price": 75, "total": 1800},
              ], subtotal=6550, tax_rate=8.25, tax_amount=540.38, total=7090.38,
              valid_until=(today + timedelta(days=15)).isoformat(),
              accepted_at=datetime.now(timezone.utc) - timedelta(days=2)),
        Quote(id=uuid.uuid4(), customer_id=customers[9].id, quote_number="Q-1003", title="Koi Pond Renovation",
              status="draft", line_items=[
                  {"description": "Pond liner replacement", "quantity": 1, "unit_price": 1200, "total": 1200},
                  {"description": "Filtration upgrade", "quantity": 1, "unit_price": 2500, "total": 2500},
                  {"description": "Aquatic plants", "quantity": 1, "unit_price": 350, "total": 350},
                  {"description": "Labor (hours)", "quantity": 12, "unit_price": 85, "total": 1020},
              ], subtotal=5070, tax_rate=8.25, tax_amount=418.28, total=5488.28,
              valid_until=(today + timedelta(days=30)).isoformat()),
        Quote(id=uuid.uuid4(), customer_id=customers[8].id, quote_number="Q-1004", title="Parking Lot Island Renovation",
              status="sent", line_items=[
                  {"description": "Remove existing plants", "quantity": 1, "unit_price": 600, "total": 600},
                  {"description": "Mexican Feathergrass x 200", "quantity": 200, "unit_price": 14, "total": 2800},
                  {"description": "Decomposed granite (tons)", "quantity": 4, "unit_price": 95, "total": 380},
                  {"description": "Drip irrigation install", "quantity": 1, "unit_price": 1500, "total": 1500},
                  {"description": "Labor (hours)", "quantity": 20, "unit_price": 75, "total": 1500},
              ], subtotal=6780, tax_rate=8.25, tax_amount=559.35, total=7339.35,
              valid_until=(today + timedelta(days=20)).isoformat()),
        Quote(id=uuid.uuid4(), customer_id=customers[14].id, quote_number="Q-1005", title="Pollinator Garden Install",
              status="declined", line_items=[
                  {"description": "Native wildflower seed mix", "quantity": 5, "unit_price": 35, "total": 175},
                  {"description": "Milkweed plants x 15", "quantity": 15, "unit_price": 12, "total": 180},
                  {"description": "Soil amendment (yards)", "quantity": 3, "unit_price": 85, "total": 255},
                  {"description": "Labor (hours)", "quantity": 6, "unit_price": 75, "total": 450},
              ], subtotal=1060, tax_rate=8.25, tax_amount=87.45, total=1147.45,
              valid_until=(today - timedelta(days=5)).isoformat()),
    ]
    db.add_all(quotes)

    # ── Invoices ───────────────────────────────────────────────────────
    invoices = []
    inv_data = [
        (customers[0], "INV-2001", "paid", 330.00, 27.23, 357.23, 357.23, today - timedelta(days=25), "Weekly mowing - March"),
        (customers[2], "INV-2002", "paid", 520.00, 42.90, 562.90, 562.90, today - timedelta(days=20), "Mulch installation"),
        (customers[5], "INV-2003", "paid", 1450.00, 119.63, 1569.63, 1569.63, today - timedelta(days=15), "Monthly estate maintenance"),
        (customers[7], "INV-2004", "sent", 2400.00, 198.00, 2598.00, 0, today + timedelta(days=10), "HOA quarterly maintenance"),
        (customers[8], "INV-2005", "sent", 1800.00, 148.50, 1948.50, 0, today + timedelta(days=15), "Commercial grounds maintenance"),
        (customers[3], "INV-2006", "paid", 275.00, 22.69, 297.69, 297.69, today - timedelta(days=10), "Xeriscaping maintenance"),
        (customers[10], "INV-2007", "overdue", 850.00, 70.13, 920.13, 0, today - timedelta(days=5), "Ranch mowing and brush control"),
        (customers[12], "INV-2008", "draft", 3200.00, 264.00, 3464.00, 0, today + timedelta(days=30), "Office courtyard renovation"),
    ]
    for inv in inv_data:
        invoice = Invoice(
            id=uuid.uuid4(), customer_id=inv[0].id, invoice_number=inv[1], status=inv[2],
            line_items=[{"description": inv[8], "quantity": 1, "unit_price": inv[3], "total": inv[3]}],
            subtotal=inv[3], tax_rate=8.25, tax_amount=inv[4], total=inv[5],
            paid_amount=inv[6], due_date=inv[7].isoformat(),
            paid_at=datetime.now(timezone.utc) - timedelta(days=5) if inv[2] == "paid" else None,
        )
        invoices.append(invoice)
    db.add_all(invoices)

    # ── Payments ───────────────────────────────────────────────────────
    payments = []
    paid_invoices = [inv for inv in invoices if inv.status == "paid"]
    methods = ["card", "check", "ach", "card"]
    for i, inv in enumerate(paid_invoices):
        p = Payment(
            id=uuid.uuid4(), invoice_id=inv.id, amount=inv.total,
            method=methods[i % len(methods)],
            reference_number=f"REF-{3000 + i}",
            paid_at=datetime.now(timezone.utc) - timedelta(days=20 - i * 3),
        )
        payments.append(p)
    # Add some partial payments
    for i in range(6):
        p = Payment(
            id=uuid.uuid4(), invoice_id=paid_invoices[i % len(paid_invoices)].id,
            amount=round(150 + i * 45.50, 2), method="card",
            paid_at=datetime.now(timezone.utc) - timedelta(days=45 - i * 5),
        )
        payments.append(p)
    db.add_all(payments)

    # ── Contracts ──────────────────────────────────────────────────────
    contracts = [
        Contract(
            id=uuid.uuid4(), customer_id=customers[0].id,
            title="Weekly Lawn Maintenance - Thompson",
            contract_type="maintenance", status="active",
            services=[
                {"description": "Mowing & edging", "included": True},
                {"description": "Trimming", "included": True},
                {"description": "Blowing", "included": True},
            ],
            price_per_visit=55, total_value=2860, visit_frequency="weekly",
            start_date=date(today.year, 3, 1).isoformat(),
            end_date=date(today.year, 11, 30).isoformat(),
            auto_renew=True,
        ),
        Contract(
            id=uuid.uuid4(), customer_id=customers[7].id,
            title="HOA Grounds Maintenance - Sunrise",
            contract_type="annual", status="active",
            services=[
                {"description": "Common area mowing", "included": True},
                {"description": "Seasonal flower rotations", "included": True},
                {"description": "Irrigation management", "included": True},
                {"description": "Tree trimming (2x/year)", "included": True},
            ],
            price_per_visit=600, total_value=24000, visit_frequency="biweekly",
            start_date=date(today.year, 1, 1).isoformat(),
            end_date=date(today.year, 12, 31).isoformat(),
            auto_renew=True,
        ),
        Contract(
            id=uuid.uuid4(), customer_id=customers[5].id,
            title="Estate Grounds - Wilson",
            contract_type="seasonal", status="active",
            services=[
                {"description": "Full property mowing", "included": True},
                {"description": "Garden bed maintenance", "included": True},
                {"description": "Hedge trimming", "included": True},
                {"description": "Seasonal plantings", "included": True},
                {"description": "Irrigation monitoring", "included": True},
            ],
            price_per_visit=350, total_value=12600, visit_frequency="weekly",
            start_date=date(today.year, 3, 1).isoformat(),
            end_date=date(today.year, 10, 31).isoformat(),
            auto_renew=False,
        ),
    ]
    db.add_all(contracts)

    # ── Equipment ──────────────────────────────────────────────────────
    equipment_data = [
        ("Scag Tiger Cat II 52\"", "mower", "Scag", "STCII-52V", "SC52-2024-1847", 2024, "available", 12500, 11000, "gasoline", 385),
        ("Scag V-Ride II 48\"", "mower", "Scag", "SVR48-II", "SC48-2023-0932", 2023, "in_use", 9800, 7500, "gasoline", 720),
        ("Stihl FS 131 Trimmer", "trimmer", "Stihl", "FS 131", "ST-FS131-4892", 2024, "available", 450, 380, "gasoline", 210),
        ("Stihl BR 800 Backpack Blower", "blower", "Stihl", "BR 800 C-E", "ST-BR800-7721", 2023, "available", 650, 520, "gasoline", 445),
        ("Ford F-350 Crew Cab", "truck", "Ford", "F-350 XLT", "1FT8W3BT5NEA12345", 2023, "in_use", 62000, 48000, "diesel", 28500),
        ("Big Tex 70PI-18 Trailer", "trailer", "Big Tex", "70PI-18", "16VPX1825N1234567", 2022, "in_use", 4200, 3200, None, 0),
        ("Husqvarna 572 XP Chainsaw", "chainsaw", "Husqvarna", "572 XP", "HQ-572-2024-2934", 2024, "available", 1100, 950, "gasoline", 85),
        ("Kubota KX040-4 Mini Excavator", "excavator", "Kubota", "KX040-4", "KB-KX040-2022-5523", 2022, "maintenance", 52000, 38000, "diesel", 1250),
    ]

    equipment = []
    for eq in equipment_data:
        e = Equipment(
            id=uuid.uuid4(), name=eq[0], equipment_type=eq[1], make=eq[2], model=eq[3],
            serial_number=eq[4], year=eq[5], status=eq[6],
            purchase_price=eq[7], current_value=eq[8], fuel_type=eq[9], hours_used=eq[10],
            purchase_date=f"{eq[5]}-01-15",
            last_maintenance_date=(today - timedelta(days=30)).isoformat(),
            next_maintenance_date=(today + timedelta(days=15)).isoformat() if eq[6] != "maintenance" else today.isoformat(),
            assigned_crew_id=crews[0].id if eq[6] == "in_use" else None,
        )
        equipment.append(e)
    db.add_all(equipment)

    # ── Time Entries ───────────────────────────────────────────────────
    time_entries = []
    for i in range(20):
        user = users[1 + (i % 4)]  # Rotate through non-admin users
        day_offset = i * 1.5
        clock_in_dt = datetime(today.year, today.month, max(1, today.day - int(day_offset)), 7, 0, tzinfo=timezone.utc)
        hours = 7.5 + (i % 3) * 0.5
        clock_out_dt = clock_in_dt + timedelta(hours=hours + 0.5)  # Extra 30 min for break
        te = TimeEntry(
            id=uuid.uuid4(), user_id=user.id,
            job_id=jobs[i % len(jobs)].id if i < len(jobs) else None,
            clock_in=clock_in_dt, clock_out=clock_out_dt,
            hours=hours, break_minutes=30,
            gps_clock_in={"lat": 30.25 + i * 0.01, "lng": -97.75 - i * 0.01},
            gps_clock_out={"lat": 30.25 + i * 0.01, "lng": -97.75 - i * 0.01},
            notes=f"Regular work day" if i % 2 == 0 else None,
        )
        time_entries.append(te)
    db.add_all(time_entries)

    # ── Leads ──────────────────────────────────────────────────────────
    leads_data = [
        ("Andrew", "Kim", "andrew.k@email.com", "(512) 555-2001", "9900 Escarpment Blvd", "Austin", "TX", "78749", "google_ads", "new", 3500, "Interested in full backyard renovation"),
        ("Priya", "Patel", "priya.p@email.com", "(512) 555-2002", "4400 Berkman Dr", "Austin", "TX", "78723", "website", "contacted", 1200, "Wants native plant garden"),
        ("Marcus", "Johnson", "marcus.j@email.com", "(512) 555-2003", "15500 Wells Port Dr", "Austin", "TX", "78728", "referral", "qualified", 8000, "New build, needs full landscape design"),
        ("Emily", "White", None, "(512) 555-2004", "2200 S Lamar Blvd", "Austin", "TX", "78704", "door_hanger", "new", 500, "Apartment complex common area"),
        ("Carlos", "Reyes", "carlos.r@email.com", "(512) 555-2005", "7700 Northcross Dr", "Austin", "TX", "78757", "social_media", "quoted", 2800, "Xeriscape conversion, water conservation"),
        ("Sandra", "O'Brien", "sandra.o@email.com", "(512) 555-2006", "11000 Research Blvd", "Austin", "TX", "78759", "google_ads", "new", 5000, "Commercial property needs landscape overhaul"),
        ("Wei", "Zhang", "wei.z@email.com", "(512) 555-2007", "3300 Bee Caves Rd", "Austin", "TX", "78746", "website", "contacted", 15000, "Luxury property, pool landscaping"),
        ("Maria", "Gonzalez", None, "(512) 555-2008", "6600 McNeil Dr", "Austin", "TX", "78729", "referral", "won", 2200, "Converted to customer, weekly mowing"),
        ("Patrick", "Sullivan", "pat.s@email.com", "(512) 555-2009", "1800 E Oltorf St", "Austin", "TX", "78741", "door_hanger", "lost", 800, "Went with competitor, price sensitive"),
        ("Yuki", "Tanaka", "yuki.t@email.com", "(512) 555-2010", "8800 Tallwood Dr", "Austin", "TX", "78759", "social_media", "new", 1800, "Interested in organic lawn care program"),
    ]

    leads = []
    for ld in leads_data:
        lead = Lead(
            id=uuid.uuid4(), first_name=ld[0], last_name=ld[1], email=ld[2], phone=ld[3],
            address=ld[4], city=ld[5], state=ld[6], zip_code=ld[7],
            source=ld[8], status=ld[9], estimated_value=ld[10], notes=ld[11],
            assigned_to=admin.id if ld[9] in ("contacted", "qualified", "quoted") else None,
        )
        leads.append(lead)
    db.add_all(leads)

    # ── Schedule Events ────────────────────────────────────────────────
    for i, job in enumerate(jobs[:10]):
        if job.scheduled_date:
            sd = datetime.fromisoformat(job.scheduled_date).replace(hour=8, tzinfo=timezone.utc)
            dur = job.estimated_duration_hours or 2
            ev = ScheduleEvent(
                id=uuid.uuid4(), job_id=job.id, crew_id=job.crew_id,
                title=job.title, start_time=sd,
                end_time=sd + timedelta(hours=dur),
                event_type="job", color=crews[i % 3].color,
            )
            db.add(ev)

    # ── System Settings ────────────────────────────────────────────────
    settings = SystemSettings(
        id=uuid.uuid4(),
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
        ],
    )
    db.add(settings)

    await db.commit()
    return {
        "users": len(users),
        "customers": len(customers),
        "crews": len(crews),
        "jobs": len(jobs),
        "inventory_items": len(inventory_items),
        "quotes": len(quotes),
        "invoices": len(invoices),
        "payments": len(payments),
        "contracts": len(contracts),
        "equipment": len(equipment),
        "time_entries": len(time_entries),
        "leads": len(leads),
    }
