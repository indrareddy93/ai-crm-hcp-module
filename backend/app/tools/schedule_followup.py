import asyncio
import uuid
from langchain_core.tools import tool
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.interaction import Interaction
from app.models.followup import Followup
from datetime import date


@tool
def schedule_followup(interaction_id: str, due_date: str, description: str) -> dict:
    """Schedule a follow-up task tied to an existing interaction.

    Args:
        interaction_id: UUID of the interaction this follow-up is linked to
        due_date: ISO date string (YYYY-MM-DD) for when the follow-up is due
        description: What the follow-up is about (e.g., "Deliver samples", "Send clinical data")

    Returns:
        Created follow-up record with id, due_date, description, status
    """
    return asyncio.get_event_loop().run_until_complete(
        _schedule_followup_async(interaction_id, due_date, description)
    )


async def _schedule_followup_async(interaction_id: str, due_date: str, description: str) -> dict:
    async with AsyncSessionLocal() as session:
        # Verify interaction exists
        stmt = select(Interaction).where(Interaction.id == interaction_id)
        result = await session.execute(stmt)
        interaction = result.scalar_one_or_none()

        if not interaction:
            return {"error": f"Interaction {interaction_id} not found."}

        # Parse date
        try:
            parsed_date = date.fromisoformat(due_date)
        except ValueError:
            return {"error": f"Invalid date format '{due_date}'. Use YYYY-MM-DD."}

        followup_id = str(uuid.uuid4())
        followup = Followup(
            id=followup_id,
            interaction_id=interaction_id,
            hcp_id=interaction.hcp_id,
            due_date=parsed_date,
            description=description,
            status="pending",
        )
        session.add(followup)
        await session.commit()

        return {
            "followup_id": followup_id,
            "interaction_id": interaction_id,
            "hcp_id": interaction.hcp_id,
            "due_date": str(parsed_date),
            "description": description,
            "status": "pending",
        }
