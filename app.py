import models
import schemas
from fastapi import FastAPI, Depends, HTTPException
from database import engine, Base, get_db
from sqlalchemy.orm import Session
from datetime import datetime

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Helpdesk API is running"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    return {"message": "DB session working"}

@app.post("/tickets", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        store=ticket.store,
        department=ticket.department,
        created_by=ticket.created_by,
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return db_ticket

@app.get("/tickets", response_model=list[schemas.TicketResponse])
def get_tickets(
    status: str = None,
    priority: str = None,
    store: str = None,
    limit: int = 10,
    offset: int = 0,
    order_by: str = "created_at",
    order_dir: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(models.Ticket)

    # filtering
    if status:
        query = query.filter(models.Ticket.status == status)

    if priority:
        query = query.filter(models.Ticket.priority == priority)

    if store:
        query = query.filter(models.Ticket.store == store)

    # sorting
    column = getattr(models.Ticket, order_by, None)

    if column is not None:
        if order_dir == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # pagination
    tickets = query.offset(offset).limit(limit).all()

    return tickets

@app.get("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket

@app.put("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
    db: Session = Depends(get_db)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # update fields if provided
    if ticket_update.status is not None:
        ticket.status = ticket_update.status

        # if status is done → set finished_at
        if ticket_update.status == "done":
            from datetime import datetime
            ticket.finished_at = datetime.utcnow()

    if ticket_update.technician is not None:
        ticket.technician = ticket_update.technician

    if ticket_update.technician_comment is not None:
        ticket.technician_comment = ticket_update.technician_comment

    # always update updated_at
    from datetime import datetime
    ticket.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    return ticket

@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted successfully"}