import asyncio
import json
from typing import Dict, Any
from langchain_core.tools import tool
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.interaction import Interaction
from app.config import get_settings


@tool
def edit_interaction(interaction_id: str, updates: Dict[str, Any]) -> dict:
    """Edit fields of an existing logged interaction.

    Args:
        interaction_id: UUID of the interaction to edit
        updates: Dict of fields to update. Allowed keys: raw_notes, outcome,
                 products_discussed, interaction_date, sentiment.
                 If raw_notes changes, AI will re-extract summary/sentiment/entities.

    Returns:
        Updated interaction record
    """
    return asyncio.get_event_loop().run_until_complete(
        _edit_interaction_async(interaction_id, updates)
    )


async def _edit_interaction_async(interaction_id: str, updates: Dict[str, Any]) -> dict:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        stmt = select(Interaction).where(Interaction.id == interaction_id)
        result = await session.execute(stmt)
        interaction = result.scalar_one_or_none()

        if not interaction:
            return {"error": f"Interaction {interaction_id} not found."}

        allowed_fields = {"raw_notes", "outcome", "products_discussed", "interaction_date", "sentiment"}
        re_extract = False

        for key, value in updates.items():
            if key not in allowed_fields:
                continue
            if key == "raw_notes" and value != interaction.raw_notes:
                re_extract = True
            setattr(interaction, key, value)

        if re_extract and interaction.raw_notes:
            extracted = await _extract_entities(interaction.raw_notes, settings.GROQ_API_KEY, settings.DEFAULT_MODEL)
            interaction.summary = extracted.get("summary", interaction.summary)
            interaction.sentiment = extracted.get("sentiment", interaction.sentiment)
            interaction.key_entities = extracted.get("key_entities", interaction.key_entities)

        await session.commit()
        await session.refresh(interaction)

        return {
            "interaction_id": interaction.id,
            "hcp_id": interaction.hcp_id,
            "summary": interaction.summary,
            "sentiment": interaction.sentiment,
            "outcome": interaction.outcome,
            "key_entities": interaction.key_entities,
            "updated": True,
        }


async def _extract_entities(raw_notes: str, api_key: str, model: str) -> dict:
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=api_key)
        prompt = f"""Extract from these notes and respond ONLY with valid JSON:
{{
  "summary": "2-3 sentence professional summary",
  "sentiment": "positive|neutral|negative",
  "key_entities": {{
    "drugs_mentioned": [],
    "competitor_products": [],
    "concerns": [],
    "commitments": []
  }}
}}

Notes: {raw_notes}"""
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=400,
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return {}
