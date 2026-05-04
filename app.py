import models
import schemas
from fastapi import FastAPI, Depends
from database import engine, Base, get_db
from sqlalchemy.orm import Session

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
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).all()
    return tickets