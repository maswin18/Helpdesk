from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Shared fields
class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"
    status: Optional[str] = "open"
    store: Optional[str] = None
    department: Optional[str] = None

# For creating ticket
class TicketCreate(TicketBase):
    created_by: str

# For updating ticket (later)
class TicketUpdate(BaseModel):
    status: Optional[str] = None
    technician: Optional[str] = None
    technician_comment: Optional[str] = None

# Response (what API returns)
class TicketResponse(TicketBase):
    id: int
    created_by: str
    technician: Optional[str]
    technician_comment: Optional[str]

    created_at: datetime
    updated_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True
