from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
import os

DB_DIR = "./data"
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = "sqlite:///./data/events.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EventDB(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    registrations = relationship("RegistrationDB", back_populates="event", cascade="all, delete-orphan")

class RegistrationDB(Base):
    __tablename__ = "registrations"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    attendee = Column(String, nullable=False)
    event = relationship("EventDB", back_populates="registrations")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Registration Web API & UI",
    version="3.0.0",
    description="Checkpoint 3: Web application with forms and resource-oriented REST API."
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class EventCreate(BaseModel):
    name: str
    capacity: int

class EventResponse(EventCreate):
    id: int
    class Config:
        from_attributes = True

class RegistrationCreate(BaseModel):
    event_id: int
    attendee: str

class RegistrationResponse(RegistrationCreate):
    id: int
    class Config:
        from_attributes = True

@app.post("/api/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def api_create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = EventDB(name=event.name, capacity=event.capacity)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/api/events", response_model=list[EventResponse])
def api_list_events(db: Session = Depends(get_db)):
    return db.query(EventDB).all()

@app.post("/api/registrations", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def api_create_registration(reg: RegistrationCreate, db: Session = Depends(get_db)):
    event = db.query(EventDB).filter(EventDB.id == reg.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    current_regs = db.query(RegistrationDB).filter(RegistrationDB.event_id == reg.event_id).count()
    if current_regs >= event.capacity:
        raise HTTPException(status_code=400, detail="Error: Cannot register, capacity limit reached.")

    db_reg = RegistrationDB(event_id=reg.event_id, attendee=reg.attendee)
    db.add(db_reg)
    db.commit()
    db.refresh(db_reg)
    return db_reg

@app.delete("/api/registrations/{reg_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_cancel_registration(reg_id: int, db: Session = Depends(get_db)):
    db_reg = db.query(RegistrationDB).filter(RegistrationDB.id == reg_id).first()
    if not db_reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    db.delete(db_reg)
    db.commit()
    return None

@app.get("/", response_class=HTMLResponse)
def web_index(request: Request, db: Session = Depends(get_db)):
    events = db.query(EventDB).all()
    registrations = db.query(RegistrationDB).all()
    
    html = f"""
    <html>
        <head>
            <title>Event Registration App</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f9f9fb; }}
                h1, h2 {{ color: #222; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; background: #fff; }}
                th, td {{ padding: 10px; border: 1px solid #ccc; text-align: left; }}
                th {{ background-color: #007bff; color: white; }}
                form {{ background: #fff; padding: 20px; border: 1px solid #ccc; margin-bottom: 20px; }}
                input, button {{ padding: 8px; margin: 5px 0; display: block; width: 100%; box-sizing: border-box; }}
                button {{ background-color: #28a745; color: white; border: none; cursor: pointer; }}
                button:hover {{ background-color: #218838; }}
                .row {{ display: flex; gap: 20px; }}
                .col {{ flex: 1; }}
            </style>
        </head>
        <body>
            <h1>Event Registration Dashboard (Checkpoint 3)</h1>
            <p>Manage events and registrations via web forms or explore the <a href="/docs" target="_blank">OpenAPI REST API Docs</a>.</p>
            <div class="row">
                <div class="col">
                    <h2>Add Event</h2>
                    <form action="/web/events" method="post">
                        <label>Name:</label><input type="text" name="name" required>
                        <label>Capacity:</label><input type="number" name="capacity" required>
                        <button type="submit">Create Event</button>
                    </form>
                    <h2>Events List</h2>
                    <table>
                        <tr><th>ID</th><th>Name</th><th>Capacity</th></tr>
                        {''.join([f"<tr><td>{e.id}</td><td>{e.name}</td><td>{e.capacity}</td></tr>" for e in events])}
                    </table>
                </div>
                <div class="col">
                    <h2>Register Attendee</h2>
                    <form action="/web/registrations" method="post">
                        <label>Event ID:</label><input type="number" name="event_id" required>
                        <label>Attendee Name:</label><input type="text" name="attendee" required>
                        <button type="submit">Register</button>
                    </form>
                    <h2>Registrations List</h2>
                    <table>
                        <tr><th>Reg ID</th><th>Event ID</th><th>Attendee</th></tr>
                        {''.join([f"<tr><td>{r.id}</td><td>{r.event_id}</td><td>{r.attendee}</td></tr>" for r in registrations])}
                    </table>
                </div>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/web/events")
def web_create_event(name: str = Form(...), capacity: int = Form(...), db: Session = Depends(get_db)):
    db.add(EventDB(name=name, capacity=capacity))
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/web/registrations")
def web_create_registration(event_id: int = Form(...), attendee: str = Form(...), db: Session = Depends(get_db)):
    event = db.query(EventDB).filter(EventDB.id == event_id).first()
    if event:
        current_regs = db.query(RegistrationDB).filter(RegistrationDB.event_id == event_id).count()
        if current_regs < event.capacity:
            db.add(RegistrationDB(event_id=event_id, attendee=attendee))
            db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)