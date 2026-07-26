"""Faker-based seed script generating 5,000+ synthetic Karnataka crime records."""

import uuid
import random
import sys
import os
from datetime import datetime, timedelta, timezone, date
from decimal import Decimal

from faker import Faker

# Add parent dir to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from app.core.database import Base
from app.core.security import hash_password
from app.models import (
    User, Officer, FIR, Accused, Victim, Investigation,
    Evidence, Witness, CriminalHistory, FinancialTransaction,
    LocationHistory,
)

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

# ─── Karnataka-specific data ────────────────────────────────────
STATIONS = [
    "Cubbon Park PS", "Whitefield PS", "Koramangala PS", "Indiranagar PS",
    "Jayanagar PS", "Basavanagudi PS", "Rajajinagar PS", "Malleswaram PS",
    "Yelahanka PS", "Electronic City PS", "HSR Layout PS", "BTM Layout PS",
    "JP Nagar PS", "Marathahalli PS", "KR Puram PS", "Hebbal PS",
    "Banashankari PS", "Vijayanagar PS", "Peenya PS", "Yeshwanthpur PS",
    "Mysuru North PS", "Mysuru South PS", "Hubli PS", "Dharwad PS",
    "Mangalore North PS", "Mangalore South PS", "Belgaum PS", "Gulbarga PS",
]

DISTRICTS = [
    "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Hubli-Dharwad",
    "Mangalore", "Belgaum", "Gulbarga", "Tumkur", "Davangere", "Shimoga",
    "Bellary", "Raichur", "Hassan", "Mandya", "Kolar",
]

RANKS = [
    "Constable", "Head Constable", "ASI", "Sub Inspector",
    "Inspector", "DySP", "SP", "DIG", "IGP",
]

FIR_TYPES = [
    "theft", "robbery", "murder", "assault", "fraud", "cybercrime",
    "kidnapping", "drug_offense", "domestic_violence", "missing_person",
    "accident", "property_dispute", "sexual_offense", "other",
]

FIR_STATUSES = [
    "open", "under_investigation", "chargesheet_filed", "closed", "reopened",
]

SEVERITIES = ["low", "medium", "high", "critical"]

IPC_SECTIONS = [
    "IPC 302", "IPC 304", "IPC 307", "IPC 376", "IPC 379", "IPC 380",
    "IPC 392", "IPC 395", "IPC 406", "IPC 420", "IPC 498A", "IPC 506",
    "IPC 354", "IPC 323", "IPC 341", "IPC 504", "IPC 509",
    "IT Act 66", "IT Act 66C", "IT Act 66D", "NDPS Act 20", "NDPS Act 22",
]

EVIDENCE_TYPES = [
    "physical", "digital", "documentary", "testimonial",
    "forensic", "photographic", "video", "audio", "other",
]

TRANSACTION_TYPES = [
    "credit", "debit", "transfer", "cash_deposit", "cash_withdrawal",
]

LOCATION_SOURCES = [
    "cell_tower", "cctv", "gps", "witness", "manual", "other",
]

BANKS = [
    "State Bank of India", "HDFC Bank", "ICICI Bank", "Canara Bank",
    "Bank of Baroda", "Punjab National Bank", "Axis Bank",
    "Union Bank of India", "Indian Bank", "Karnataka Bank",
]

OCCUPATIONS = [
    "Daily Wage Laborer", "Auto Rickshaw Driver", "Software Engineer",
    "Business Owner", "Student", "Farmer", "Teacher", "Unemployed",
    "Construction Worker", "Delivery Executive", "Mechanic",
    "Security Guard", "Shopkeeper", "Government Employee",
]

OFFENSE_TYPES = [
    "Petty Theft", "Chain Snatching", "Burglary", "Assault",
    "Drug Possession", "Fraud", "Domestic Violence", "DUI",
    "Vandalism", "Trespassing", "Extortion",
]

COURTS = [
    "Bengaluru City Civil Court", "Mysuru Sessions Court",
    "Karnataka High Court", "Hubli JMFC Court",
    "Mangalore District Court", "Belgaum Sessions Court",
]

BENGALURU_COORDS = {
    "lat_range": (12.85, 13.10),
    "lng_range": (77.50, 77.75),
}


def random_date(start_year: int = 2022, end_year: int = 2025) -> date:
    """Generate a random date in range."""
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def random_datetime(start_year: int = 2022, end_year: int = 2025) -> datetime:
    """Generate a random datetime in range."""
    d = random_date(start_year, end_year)
    return datetime(
        d.year, d.month, d.day,
        random.randint(0, 23), random.randint(0, 59),
        tzinfo=timezone.utc,
    )


def random_coords():
    """Generate random coordinates around Bengaluru."""
    lat = random.uniform(*BENGALURU_COORDS["lat_range"])
    lng = random.uniform(*BENGALURU_COORDS["lng_range"])
    return round(lat, 6), round(lng, 6)


def seed_database(database_url: str):
    """Seed the database with synthetic data."""
    engine = create_engine(database_url)

    # Disable prepared statements for Supabase/PgBouncer compatibility
    @event.listens_for(engine, "connect")
    def _set_pg_prepare_threshold(dbapi_conn, connection_record):
        if hasattr(dbapi_conn, "prepare_threshold"):
            dbapi_conn.prepare_threshold = 0

    # Drop existing tables to allow re-running seed script cleanly
    print("[*] Clearing existing tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        print("[*] Seeding users...")
        users = seed_users(session)

        print("[*] Seeding officers...")
        officers = seed_officers(session, count=80)

        print("[*] Seeding FIRs...")
        firs = seed_firs(session, officers, count=1000)

        print("[*] Seeding accused...")
        accused_list = seed_accused(session, firs, count=1500)

        print("[*] Seeding victims...")
        seed_victims(session, firs, count=1200)

        print("[*] Seeding investigations...")
        seed_investigations(session, firs, officers, count=800)

        print("[*] Seeding evidence...")
        seed_evidence(session, firs, officers, count=1500)

        print("[*] Seeding witnesses...")
        seed_witnesses(session, firs, count=900)

        print("[*] Seeding criminal histories...")
        seed_criminal_history(session, accused_list, count=600)

        print("[*] Seeding financial transactions...")
        seed_financial_transactions(session, firs, accused_list, count=800)

        print("[*] Seeding location histories...")
        seed_location_history(session, firs, accused_list, count=1000)

        session.commit()
        print("\n[+] Database seeded successfully!")
        print(f"   Total records: ~{sum([
            len(users), 80, 1000, 1500, 1200, 800, 1500, 900, 600, 800, 1000
        ]):,}")


def seed_users(session: Session) -> list:
    """Create demo users for auth."""
    demo_users = [
        User(
            username="admin",
            email="admin@ksp.gov.in",
            hashed_password=hash_password("admin123"),
            full_name="Dr. Rajesh Kumar IPS",
            role="admin",
            badge_number="KSP-001",
            department="Crime Investigation Department",
        ),
        User(
            username="officer1",
            email="officer1@ksp.gov.in",
            hashed_password=hash_password("officer123"),
            full_name="Inspector Priya Sharma",
            role="officer",
            badge_number="KSP-102",
            department="Law and Order",
        ),
        User(
            username="analyst",
            email="analyst@ksp.gov.in",
            hashed_password=hash_password("analyst123"),
            full_name="Arun Patil",
            role="analyst",
            badge_number="KSP-201",
            department="Data Analytics Wing",
        ),
    ]
    session.add_all(demo_users)
    session.flush()
    return demo_users


def seed_officers(session: Session, count: int = 80) -> list:
    """Generate officers across Karnataka stations."""
    officers = []
    for i in range(count):
        officer = Officer(
            name=fake.name(),
            badge_number=f"KSP-{1000 + i}",
            rank=random.choice(RANKS),
            department=random.choice([
                "Law and Order", "Crime Investigation Department",
                "Traffic", "Cybercrime", "Narcotics", "Special Branch",
            ]),
            station=random.choice(STATIONS),
            phone=fake.phone_number(),
            email=fake.email(),
            date_of_joining=random_date(2005, 2023),
            is_active=random.random() > 0.1,
        )
        officers.append(officer)
    session.add_all(officers)
    session.flush()
    return officers


def seed_firs(session: Session, officers: list, count: int = 1000) -> list:
    """Generate FIR records."""
    firs = []
    for i in range(count):
        lat, lng = random_coords()
        fir_date = random_date(2022, 2025)
        station = random.choice(STATIONS)
        district = random.choice(DISTRICTS)

        fir = FIR(
            fir_number=f"KSP/{district[:3].upper()}/{fir_date.year}/{i + 1:04d}",
            title=fake.sentence(nb_words=8),
            description=fake.paragraph(nb_sentences=4),
            fir_date=fir_date,
            fir_type=random.choice(FIR_TYPES),
            status=random.choice(FIR_STATUSES),
            severity=random.choices(
                SEVERITIES, weights=[30, 40, 20, 10]
            )[0],
            ipc_sections=random.sample(IPC_SECTIONS, k=random.randint(1, 3)),
            station=station,
            district=district,
            state="Karnataka",
            latitude=lat,
            longitude=lng,
            reporting_officer_id=random.choice(officers).id,
            investigating_officer_id=random.choice(officers).id,
        )
        firs.append(fir)
    session.add_all(firs)
    session.flush()
    return firs


def seed_accused(session: Session, firs: list, count: int = 1500) -> list:
    """Generate accused records linked to FIRs."""
    accused_list = []
    for _ in range(count):
        fir = random.choice(firs)
        is_arrested = random.random() > 0.4
        arrest_date = (
            random_date(fir.fir_date.year, 2025) if is_arrested else None
        )
        bail_choices = ["bail_granted", "bail_denied", "bail_pending"]

        accused = Accused(
            fir_id=fir.id,
            name=fake.name(),
            alias=fake.first_name() if random.random() > 0.7 else None,
            age=random.randint(18, 65),
            gender=random.choice(["male", "female", "other"]),
            address=fake.address(),
            phone=fake.phone_number(),
            id_type=random.choice(["Aadhaar", "PAN", "Voter ID", "Passport"]),
            id_number=fake.bothify("????-####-####"),
            occupation=random.choice(OCCUPATIONS),
            is_arrested=is_arrested,
            arrest_date=arrest_date,
            bail_status=(
                random.choice(bail_choices) if is_arrested else "not_applicable"
            ),
        )
        accused_list.append(accused)
    session.add_all(accused_list)
    session.flush()
    return accused_list


def seed_victims(session: Session, firs: list, count: int = 1200):
    """Generate victim records linked to FIRs."""
    victims = []
    for _ in range(count):
        fir = random.choice(firs)
        victims.append(Victim(
            fir_id=fir.id,
            name=fake.name(),
            age=random.randint(5, 80),
            gender=random.choice(["male", "female", "other"]),
            address=fake.address(),
            phone=fake.phone_number(),
            injury_type=random.choice([
                "Bruises", "Fracture", "Laceration", "Burns",
                "Head Injury", "Internal Bleeding", "None", "Gunshot",
            ]),
            injury_severity=random.choice([
                "none", "minor", "moderate", "severe", "fatal",
            ]),
            hospital_name=random.choice([
                "Victoria Hospital", "Manipal Hospital", "Narayana Health",
                "Apollo Hospital", "Columbia Asia", "Fortis Hospital",
                None, None,
            ]),
            is_minor=random.random() > 0.85,
        ))
    session.add_all(victims)
    session.flush()


def seed_investigations(
    session: Session, firs: list, officers: list, count: int = 800
):
    """Generate investigation records."""
    investigations = []
    for _ in range(count):
        fir = random.choice(firs)
        started = random_date(fir.fir_date.year, 2025)
        status = random.choice([
            "in_progress", "completed", "pending_review", "on_hold",
        ])
        completed = (
            random_date(started.year, 2025)
            if status == "completed" else None
        )
        investigations.append(Investigation(
            fir_id=fir.id,
            officer_id=random.choice(officers).id,
            description=fake.paragraph(nb_sentences=3),
            findings=(
                fake.paragraph(nb_sentences=5) if status == "completed" else None
            ),
            status=status,
            started_at=started,
            completed_at=completed,
        ))
    session.add_all(investigations)
    session.flush()


def seed_evidence(
    session: Session, firs: list, officers: list, count: int = 1500
):
    """Generate evidence records."""
    evidence_items = []
    for _ in range(count):
        fir = random.choice(firs)
        evidence_items.append(Evidence(
            fir_id=fir.id,
            evidence_type=random.choice(EVIDENCE_TYPES),
            description=fake.sentence(nb_words=12),
            collected_by=random.choice(officers).id,
            collected_at=random_datetime(fir.fir_date.year, 2025),
            storage_location=f"Locker-{random.randint(1, 500):03d}",
            chain_of_custody=fake.sentence(nb_words=8),
            is_verified=random.random() > 0.3,
        ))
    session.add_all(evidence_items)
    session.flush()


def seed_witnesses(session: Session, firs: list, count: int = 900):
    """Generate witness records."""
    witnesses = []
    for _ in range(count):
        fir = random.choice(firs)
        witnesses.append(Witness(
            fir_id=fir.id,
            name=fake.name(),
            age=random.randint(18, 75),
            gender=random.choice(["male", "female", "other"]),
            address=fake.address(),
            phone=fake.phone_number(),
            statement=fake.paragraph(nb_sentences=4),
            statement_date=random_date(fir.fir_date.year, 2025),
            is_reliable=random.random() > 0.15,
            protection_needed=random.random() > 0.85,
        ))
    session.add_all(witnesses)
    session.flush()


def seed_criminal_history(
    session: Session, accused_list: list, count: int = 600
):
    """Generate criminal history records."""
    records = []
    for _ in range(count):
        accused = random.choice(accused_list)
        records.append(CriminalHistory(
            accused_id=accused.id,
            offense_type=random.choice(OFFENSE_TYPES),
            case_number=f"CC/{random.randint(2015, 2024)}/{random.randint(1, 9999):04d}",
            court_name=random.choice(COURTS),
            conviction_date=random_date(2015, 2024),
            sentence=random.choice([
                "6 months imprisonment", "1 year imprisonment",
                "2 years imprisonment", "Fine of ₹50,000",
                "Fine of ₹1,00,000", "3 years imprisonment",
                "Community service", "Probation 1 year",
            ]),
            status=random.choice(["recorded", "convicted", "acquitted", "pending"]),
            remarks=fake.sentence(nb_words=6) if random.random() > 0.5 else None,
        ))
    session.add_all(records)
    session.flush()


def seed_financial_transactions(
    session: Session, firs: list, accused_list: list, count: int = 800
):
    """Generate financial transaction records."""
    transactions = []
    for _ in range(count):
        fir = random.choice(firs)
        accused = random.choice(accused_list) if random.random() > 0.3 else None
        transactions.append(FinancialTransaction(
            fir_id=fir.id,
            accused_id=accused.id if accused else None,
            transaction_type=random.choice(TRANSACTION_TYPES),
            amount=Decimal(str(round(random.uniform(500, 5000000), 2))),
            currency="INR",
            from_account=fake.bothify("####-####-####-####"),
            to_account=fake.bothify("####-####-####-####"),
            bank_name=random.choice(BANKS),
            transaction_date=random_datetime(fir.fir_date.year, 2025),
            is_suspicious=random.random() > 0.75,
            remarks=fake.sentence(nb_words=6) if random.random() > 0.5 else None,
        ))
    session.add_all(transactions)
    session.flush()


def seed_location_history(
    session: Session, firs: list, accused_list: list, count: int = 1000
):
    """Generate location history records."""
    locations_list = []
    bengaluru_places = [
        "MG Road", "Brigade Road", "Commercial Street", "Cubbon Park",
        "Lalbagh", "Vidhana Soudha", "Majestic Bus Stand", "KR Market",
        "Forum Mall", "Mantri Square", "UB City", "Phoenix Marketcity",
        "Bannerghatta Road", "Outer Ring Road", "Silk Board Junction",
        "Hebbal Flyover", "Yeshwanthpur APMC", "Peenya Industrial Area",
    ]

    for _ in range(count):
        accused = random.choice(accused_list)
        fir = random.choice(firs) if random.random() > 0.3 else None
        lat, lng = random_coords()
        locations_list.append(LocationHistory(
            accused_id=accused.id,
            fir_id=fir.id if fir else None,
            location_name=random.choice(bengaluru_places),
            address=fake.address(),
            latitude=lat,
            longitude=lng,
            recorded_at=random_datetime(2022, 2025),
            source=random.choice(LOCATION_SOURCES),
            remarks=fake.sentence(nb_words=5) if random.random() > 0.6 else None,
        ))
    session.add_all(locations_list)
    session.flush()


if __name__ == "__main__":
    from app.core.config import settings
    db_url = settings.DATABASE_URL_SYNC
    print(f"[*] Connecting to: {db_url}")
    seed_database(db_url)
