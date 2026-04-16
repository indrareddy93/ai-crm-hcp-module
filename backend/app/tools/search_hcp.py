import asyncio
from typing import List
from langchain_core.tools import tool
from sqlalchemy import select, or_, func
from app.db.session import AsyncSessionLocal
from app.models.hcp import HCP


@tool
def search_hcp(query: str, limit: int = 5) -> List[dict]:
    """Search for Healthcare Professionals (HCPs) by name, specialty, or hospital.
    Use this tool when you need to find an HCP's ID before logging or editing an interaction.

    Args:
        query: Search string (name, specialty, or hospital)
        limit: Maximum number of results to return (default 5)

    Returns:
        List of matching HCP records with id, name, specialty, hospital, city
    """
    return asyncio.get_event_loop().run_until_complete(_search_hcp_async(query, limit))


async def _search_hcp_async(query: str, limit: int) -> List[dict]:
    async with AsyncSessionLocal() as session:
        q = f"%{query.lower()}%"
        stmt = select(HCP).where(
            or_(
                func.lower(HCP.first_name).like(q),
                func.lower(HCP.last_name).like(q),
                func.lower(func.concat(HCP.first_name, " ", HCP.last_name)).like(q),
                func.lower(HCP.specialty).like(q),
                func.lower(HCP.hospital).like(q),
                func.lower(HCP.city).like(q),
            )
        ).limit(limit)
        result = await session.execute(stmt)
        hcps = result.scalars().all()
        return [
            {
                "id": h.id,
                "name": f"{h.first_name} {h.last_name}",
                "specialty": h.specialty,
                "hospital": h.hospital,
                "city": h.city,
                "email": h.email,
            }
            for h in hcps
        ]
