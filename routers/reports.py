from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
from database import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):

    total = db.query(func.count(models.Ticket.id)).scalar()

    open_count = db.query(func.count(models.Ticket.id)) \
        .filter(models.Ticket.status == "open") \
        .scalar()
    
    done_count = db.query(func.count(models.Ticket.id)) \
        .filter(models.Ticket.status == "done") \
        .scalar()
    
    technician_stats = db.query(
        models.Ticket.technician,
        func.count(models.Ticket.id)
    ).group_by(models.Ticket.technician).all()

    avg_resolution = db.query(
        func.avg(
            func.strftime('%s', models.Ticket.finished_at) -
            func.strftime('%s', models.Ticket.created_at)
        )
    ).filter(models.Ticket.finished_at != None).scalar()

    return {
        "total_tickets": total,
        "open_tickets": open_count,
        "done_tickets": done_count,
        "tickets_per_technician": [
            {"technician": t[0], "total": t[1]} for t in technician_stats
        ],
        "avg_resolution_seconds": avg_resolution
    }