from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HCPBase(BaseModel):
    first_name: str
    last_name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPOut(HCPBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
