from fastapi import FastAPI
from database import engine, Base

from routers import tickets, reports

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(tickets.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"message": "Helpdesk API is running"}