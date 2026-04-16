from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime


class InteractionCreate(BaseModel):
    hcp_id: str
    interaction_type: str = "in_person"
    interaction_date: Optional[datetime] = None
    products_discussed: Optional[List[str]] = []
    raw_notes: Optional[str] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = "neutral"
    source: str = "form"


class InteractionUpdate(BaseModel):
    interaction_type: Optional[str] = None
    interaction_date: Optional[datetime] = None
    products_discussed: Optional[List[str]] = None
    raw_notes: Optional[str] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    key_entities: Optional[Dict[str, Any]] = None


class InteractionOut(BaseModel):
    id: str
    hcp_id: str
    interaction_type: str
    interaction_date: datetime
    products_discussed: Optional[List[str]] = []
    summary: Optional[str] = None
    raw_notes: Optional[str] = None
    sentiment: Optional[str] = None
    key_entities: Optional[Dict[str, Any]] = None
    outcome: Optional[str] = None
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
