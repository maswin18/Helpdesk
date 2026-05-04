from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    priority = Column(String, default="normal") # low, normal, high
    status = Column(String, default="open") # open, pending, hold, done

    store = Column(String, nullable=True)
    department = Column(String, nullable=True)

    created_by = Column(String, nullable=False)
    technician = Column(String, nullable=True)
    technician_comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)