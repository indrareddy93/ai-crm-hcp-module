import asyncio
from typing import List
from langchain_core.tools import tool
from sqlalchemy import select, or_, func, desc
from app.db.session import AsyncSessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction


@tool
def get_interaction_history(hcp_id_or_name: str, limit: int = 10) -> List[dict]:
    """Retrieve recent interactions for an HCP by their ID or name.

    Args:
        hcp_id_or_name: HCP UUID or full/partial name (e.g., "Dr. Sharma", "Patel")
        limit: Max number of interactions to return (default 10)

    Returns:
        List of interaction summaries sorted by most recent first
    """
    return asyncio.get_event_loop().run_until_complete(
        _get_history_async(hcp_id_or_name, limit)
    )


async def _get_history_async(hcp_id_or_name: str, limit: int) -> List[dict]:
    async with AsyncSessionLocal() as session:
        # Try as UUID first
        hcp_id = None
        try:
            import uuid
            uuid.UUID(hcp_id_or_name)
            hcp_id = hcp_id_or_name
        except ValueError:
            # Search by name
            q = f"%{hcp_id_or_name.lower().replace('dr.', '').replace('dr ', '').strip()}%"
            stmt = select(HCP).where(
                or_(
                    func.lower(HCP.first_name).like(q),
                    func.lower(HCP.last_name).like(q),
                    func.lower(func.concat(HCP.first_name, " ", HCP.last_name)).like(q),
                )
            ).limit(1)
            result = await session.execute(stmt)
            hcp = result.scalar_one_or_none()
            if not hcp:
                return [{"error": f"No HCP found matching '{hcp_id_or_name}'"}]
            hcp_id = hcp.id

        # Get interactions
        stmt = (
            select(Interaction)
            .where(Interaction.hcp_id == hcp_id)
            .order_by(desc(Interaction.interaction_date))
            .limit(limit)
        )
        result = await session.execute(stmt)
        interactions = result.scalars().all()

        # Get HCP name
        hcp_stmt = select(HCP).where(HCP.id == hcp_id)
        hcp_result = await session.execute(hcp_stmt)
        hcp = hcp_result.scalar_one_or_none()
        hcp_name = f"{hcp.first_name} {hcp.last_name}" if hcp else "Unknown"

        return [
            {
                "interaction_id": i.id,
                "hcp_name": hcp_name,
                "hcp_id": i.hcp_id,
                "date": i.interaction_date.isoformat() if i.interaction_date else None,
                "type": i.interaction_type,
                "summary": i.summary or i.raw_notes[:200] if i.raw_notes else None,
                "sentiment": i.sentiment,
                "products_discussed": i.products_discussed or [],
                "outcome": i.outcome,
                "source": i.source,
            }
            for i in interactions
        ]
