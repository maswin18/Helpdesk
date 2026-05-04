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