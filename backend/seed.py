"""
Seed script — inserts 10 realistic HCPs and 5 sample interactions.
Run from the backend/ directory:
    python seed.py
"""
import asyncio
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import AsyncSessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction
from datetime import datetime, timezone, timedelta


HCP_DATA = [
    {"first_name": "Priya", "last_name": "Sharma", "specialty": "Cardiology", "hospital": "Apollo Hospitals", "city": "Hyderabad", "email": "p.sharma@apollo.in", "phone": "+91-9876543210"},
    {"first_name": "Rajesh", "last_name": "Patel", "specialty": "Endocrinology", "hospital": "Fortis Healthcare", "city": "Mumbai", "email": "r.patel@fortis.in", "phone": "+91-9876543211"},
    {"first_name": "Ananya", "last_name": "Mehta", "specialty": "Neurology", "hospital": "AIIMS Delhi", "city": "New Delhi", "email": "a.mehta@aiims.edu", "phone": "+91-9876543212"},
    {"first_name": "Suresh", "last_name": "Kumar", "specialty": "Oncology", "hospital": "Tata Memorial Centre", "city": "Mumbai", "email": "s.kumar@tmc.gov.in", "phone": "+91-9876543213"},
    {"first_name": "James", "last_name": "Harrison", "specialty": "Cardiology", "hospital": "Cleveland Clinic", "city": "Cleveland", "email": "j.harrison@ccf.org", "phone": "+1-216-555-0101"},
    {"first_name": "Sarah", "last_name": "Mitchell", "specialty": "Endocrinology", "hospital": "Mayo Clinic", "city": "Rochester", "email": "s.mitchell@mayo.edu", "phone": "+1-507-555-0102"},
    {"first_name": "David", "last_name": "Chen", "specialty": "Pulmonology", "hospital": "Johns Hopkins Hospital", "city": "Baltimore", "email": "d.chen@jhmi.edu", "phone": "+1-410-555-0103"},
    {"first_name": "Fatima", "last_name": "Al-Rashid", "specialty": "Rheumatology", "hospital": "Aster Medcity", "city": "Kochi", "email": "f.alrashid@asterhospitals.in", "phone": "+91-9876543214"},
    {"first_name": "Vikram", "last_name": "Singh", "specialty": "Gastroenterology", "hospital": "Medanta Medicity", "city": "Gurugram", "email": "v.singh@medanta.org", "phone": "+91-9876543215"},
    {"first_name": "Emily", "last_name": "Johnson", "specialty": "Dermatology", "hospital": "Stanford Health Care", "city": "Stanford", "email": "e.johnson@stanford.edu", "phone": "+1-650-555-0104"},
]

INTERACTION_TEMPLATES = [
    {
        "interaction_type": "in_person",
        "raw_notes": "Met with Dr. Sharma to discuss Atorvastatin 20mg efficacy in high-risk cardiac patients. She was very receptive and requested sample packs. Mentioned competitor Rosuvastatin being pushed by rival reps.",
        "products_discussed": ["Atorvastatin 20mg", "Lipitor"],
        "summary": "Productive in-person meeting discussing Atorvastatin efficacy. Dr. Sharma is interested in samples and open to prescribing for high-risk patients.",
        "sentiment": "positive",
        "key_entities": {"drugs_mentioned": ["Atorvastatin 20mg", "Lipitor"], "competitor_products": ["Rosuvastatin"], "concerns": [], "commitments": ["Deliver sample packs next visit"]},
        "outcome": "Requested sample packs; follow-up scheduled",
    },
    {
        "interaction_type": "virtual",
        "raw_notes": "Video call with Dr. Patel about Metformin XR for Type 2 diabetes. He has concerns about GI side effects in elderly patients. Wants clinical data comparing XR vs standard formulation.",
        "products_discussed": ["Metformin XR", "Metformin 500mg"],
        "summary": "Virtual meeting regarding Metformin XR. Dr. Patel raised GI tolerability concerns for elderly patients and requested comparative clinical data.",
        "sentiment": "neutral",
        "key_entities": {"drugs_mentioned": ["Metformin XR", "Metformin 500mg"], "competitor_products": [], "concerns": ["GI side effects in elderly"], "commitments": ["Send comparative clinical study"]},
        "outcome": "Clinical data to be sent via email",
    },
    {
        "interaction_type": "phone",
        "raw_notes": "Quick call with Dr. Mehta. She reported good outcomes with Levetiracetam in seizure patients. Interested in new extended-release formulation. Negative on Valproate due to teratogenicity concerns.",
        "products_discussed": ["Levetiracetam", "Levetiracetam XR"],
        "summary": "Phone follow-up with Dr. Mehta confirming positive outcomes with Levetiracetam. Interest in XR formulation noted; teratogenicity concerns around Valproate documented.",
        "sentiment": "positive",
        "key_entities": {"drugs_mentioned": ["Levetiracetam", "Levetiracetam XR", "Valproate"], "competitor_products": [], "concerns": ["Teratogenicity with Valproate"], "commitments": []},
        "outcome": "Share XR formulation brochure",
    },
    {
        "interaction_type": "in_person",
        "raw_notes": "Visited Dr. Harrison at Cleveland Clinic. Discussed Sacubitril/Valsartan for HFrEF patients. He was enthusiastic but concerned about hypotension in older patients. Agreed to trial in 5 patients.",
        "products_discussed": ["Sacubitril/Valsartan", "Entresto"],
        "summary": "Productive visit at Cleveland Clinic. Dr. Harrison is enthusiastic about Entresto for HFrEF but flagged hypotension risk. Plans to initiate trial in 5 patients.",
        "sentiment": "positive",
        "key_entities": {"drugs_mentioned": ["Sacubitril/Valsartan", "Entresto"], "competitor_products": [], "concerns": ["Hypotension in elderly HFrEF patients"], "commitments": ["Trial in 5 patients next month"]},
        "outcome": "Trial initiated; follow-up in 4 weeks",
    },
    {
        "interaction_type": "email",
        "raw_notes": "Email exchange with Dr. Mitchell regarding Semaglutide for obesity management. She is cautious — wants more real-world evidence beyond clinical trials. Will consider after reviewing STEP trial data.",
        "products_discussed": ["Semaglutide", "Ozempic"],
        "summary": "Email discussion about Semaglutide for obesity. Dr. Mitchell is cautious and wants real-world evidence. Reviewing STEP trial data before making prescribing decision.",
        "sentiment": "neutral",
        "key_entities": {"drugs_mentioned": ["Semaglutide", "Ozempic"], "competitor_products": [], "concerns": ["Lack of real-world evidence"], "commitments": ["Send STEP trial paper"]},
        "outcome": "Send real-world evidence paper; follow-up in 2 weeks",
    },
]


async def seed():
    print("Starting seed...")
    async with AsyncSessionLocal() as session:
        hcp_ids = []
        for data in HCP_DATA:
            hcp = HCP(id=str(uuid.uuid4()), **data)
            session.add(hcp)
            hcp_ids.append(hcp.id)
            print(f"  Added HCP: Dr. {data['first_name']} {data['last_name']}")

        await session.flush()

        now = datetime.now(timezone.utc)
        for i, template in enumerate(INTERACTION_TEMPLATES):
            interaction = Interaction(
                id=str(uuid.uuid4()),
                hcp_id=hcp_ids[i],
                interaction_date=now - timedelta(days=i * 3),
                source="form",
                **template,
            )
            session.add(interaction)
            print(f"  Added interaction for HCP {i + 1}")

        await session.commit()
        print(f"\nSeeded {len(HCP_DATA)} HCPs and {len(INTERACTION_TEMPLATES)} interactions successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
