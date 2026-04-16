import uuid
import json
from typing import List
from langchain_core.tools import tool
from sqlalchemy import select, or_, func
from app.db.session import AsyncSessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.config import get_settings


@tool
async def log_interaction(
    hcp_name: str,
    raw_notes: str,
    interaction_type: str = "in_person",
    products_discussed: List[str] = [],
) -> dict:
    """Log a new interaction with an HCP. Extracts summary, sentiment, and key entities using AI.

    Args:
        hcp_name: Full or partial name of the HCP (e.g. "Dr. Sharma", "Patel")
        raw_notes: The rep's notes from the meeting
        interaction_type: One of: in_person, virtual, phone, email
        products_discussed: List of product/drug names mentioned

    Returns:
        dict with interaction_id, summary, sentiment, key_entities, and hcp info
    """
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        # Find HCP by fuzzy name match
        q = f"%{hcp_name.lower().replace('dr.', '').replace('dr ', '').strip()}%"
        stmt = select(HCP).where(
            or_(
                func.lower(HCP.first_name).like(q),
                func.lower(HCP.last_name).like(q),
                func.lower(func.concat(HCP.first_name, " ", HCP.last_name)).like(q),
            )
        ).limit(5)
        result = await session.execute(stmt)
        hcps = result.scalars().all()

        if not hcps:
            return {"error": f"No HCP found matching '{hcp_name}'. Please use search_hcp first."}

        if len(hcps) > 1:
            return {
                "ambiguous": True,
                "message": f"Multiple HCPs found for '{hcp_name}'. Please specify which one:",
                "options": [
                    {"id": h.id, "name": f"{h.first_name} {h.last_name}", "specialty": h.specialty, "hospital": h.hospital}
                    for h in hcps
                ],
            }

        hcp = hcps[0]

        # Extract entities via Groq
        extracted = await _extract_entities(raw_notes, settings.GROQ_API_KEY, settings.DEFAULT_MODEL)

        interaction_id = str(uuid.uuid4())
        interaction = Interaction(
            id=interaction_id,
            hcp_id=hcp.id,
            interaction_type=interaction_type,
            products_discussed=products_discussed or extracted.get("products", []),
            raw_notes=raw_notes,
            summary=extracted.get("summary", raw_notes[:200]),
            sentiment=extracted.get("sentiment", "neutral"),
            key_entities=extracted.get("key_entities", {}),
            source="chat",
        )
        session.add(interaction)
        await session.commit()

        return {
            "interaction_id": interaction_id,
            "hcp": f"{hcp.first_name} {hcp.last_name}",
            "hcp_id": hcp.id,
            "summary": interaction.summary,
            "sentiment": interaction.sentiment,
            "key_entities": interaction.key_entities,
            "interaction_type": interaction_type,
        }


async def _extract_entities(raw_notes: str, api_key: str, model: str) -> dict:
    """Call Groq to extract summary, sentiment, and key entities from raw notes."""
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=api_key)

        prompt = f"""Extract the following from these field rep notes and respond ONLY with valid JSON:
{{
  "summary": "2-3 sentence professional summary of the interaction",
  "sentiment": "positive|neutral|negative",
  "key_entities": {{
    "drugs_mentioned": ["list", "of", "drug names"],
    "competitor_products": ["list of competitor products if any"],
    "concerns": ["list of HCP concerns or objections"],
    "commitments": ["list of follow-up commitments made"]
  }},
  "products": ["list of products discussed"]
}}

Notes: {raw_notes}

Respond with ONLY the JSON object, no markdown, no explanation."""

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )
        text = response.choices[0].message.content.strip()
        # Strip markdown if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        return {
            "summary": raw_notes[:300],
            "sentiment": "neutral",
            "key_entities": {"error": str(e)},
            "products": [],
        }
