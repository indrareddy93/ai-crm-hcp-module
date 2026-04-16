import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from app.db.session import get_db
from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate, InteractionUpdate, InteractionOut

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.get("", response_model=List[InteractionOut])
async def list_interactions(
    hcp_id: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Interaction).order_by(desc(Interaction.created_at))
    if hcp_id:
        stmt = stmt.where(Interaction.hcp_id == hcp_id)
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=InteractionOut, status_code=201)
async def create_interaction(
    payload: InteractionCreate, db: AsyncSession = Depends(get_db)
):
    from datetime import datetime, timezone
    interaction = Interaction(
        id=str(uuid.uuid4()),
        hcp_id=payload.hcp_id,
        interaction_type=payload.interaction_type,
        interaction_date=payload.interaction_date or datetime.now(timezone.utc),
        products_discussed=payload.products_discussed or [],
        raw_notes=payload.raw_notes,
        sentiment=payload.sentiment or "neutral",
        outcome=payload.outcome,
        source=payload.source,
    )
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)
    return interaction


@router.get("/{interaction_id}", response_model=InteractionOut)
async def get_interaction(interaction_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Interaction).where(Interaction.id == interaction_id))
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.patch("/{interaction_id}", response_model=InteractionOut)
async def update_interaction(
    interaction_id: str,
    payload: InteractionUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interaction).where(Interaction.id == interaction_id))
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(interaction, key, value)

    await db.commit()
    await db.refresh(interaction)
    return interaction
