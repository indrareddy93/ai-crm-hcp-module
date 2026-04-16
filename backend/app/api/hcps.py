from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional
from app.db.session import get_db
from app.models.hcp import HCP
from app.schemas.hcp import HCPCreate, HCPOut

router = APIRouter(prefix="/hcps", tags=["hcps"])


@router.get("", response_model=List[HCPOut])
async def list_hcps(
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(HCP)
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(HCP.first_name).like(pattern),
                func.lower(HCP.last_name).like(pattern),
                func.lower(func.concat(HCP.first_name, " ", HCP.last_name)).like(pattern),
                func.lower(HCP.specialty).like(pattern),
                func.lower(HCP.hospital).like(pattern),
                func.lower(HCP.city).like(pattern),
            )
        )
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=HCPOut, status_code=201)
async def create_hcp(payload: HCPCreate, db: AsyncSession = Depends(get_db)):
    import uuid
    hcp = HCP(id=str(uuid.uuid4()), **payload.model_dump())
    db.add(hcp)
    await db.commit()
    await db.refresh(hcp)
    return hcp


@router.get("/{hcp_id}", response_model=HCPOut)
async def get_hcp(hcp_id: str, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp
