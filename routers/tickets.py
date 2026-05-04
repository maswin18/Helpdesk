from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas
from database import get_db

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_ticket = models.Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.get("", response_model=list[schemas.TicketResponse])
def get_tickets(
    status: str = None,
    priority: str = None,
    store: str = None,
    from_date: str = None,
    to_date: str = None,
    limit: int = 10,
    offset: int = 0,
    order_by: str = "created_at",
    order_dir: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(models.Ticket)

    if status:
        query = query.filter(models.Ticket.status == status)

    if priority:
        query = query.filter(models.Ticket.priority == priority)

    if store:
        query = query.filter(models.Ticket.store == store)

    if from_date:
        try:
            query = query.filter(models.Ticket.created_at >= datetime.fromisoformat(from_date))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid from_date format")
        
    if to_date:
        try:
            query = query.filter(models.Ticket.created_at <= datetime.fromisoformat(to_date))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid to_date format")
    
    allowed_fields = ["id", "created_at", "priority", "status"]
    if order_by in allowed_fields:
        column = getattr(models.Ticket, order_by)
        query = query.order_by(column.desc() if order_dir == "desc" else column.asc())

    return query.offset(offset).limit(limit).all()


@router.get("/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}", response_model=schemas.TicketResponse)
def update_ticket(ticket_id: int, ticket_update: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket_update.status is not None:
        ticket.status = ticket_update.status
        if ticket_update.status == "done":
            ticket.finished_at = datetime.utcnow()

    if ticket_update.technician is not None:
        ticket.technician = ticket_update.technician

    if ticket_update.technician_comment is not None:
        ticket.technician_comment = ticket_update.technician_comment

    ticket.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    return ticket


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted successfully"}
