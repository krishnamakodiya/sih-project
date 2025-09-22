from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db, Base, engine
from models import User, Classroom, Attendance, FocusMode
from schemas import UserCreate, UserLogin, AttendanceCreate, FocusModeCreate, ClassroomResponse
from auth import hash_password, verify_password, create_access_token, get_current_user

# ------------------ CREATE TABLES ------------------
Base.metadata.create_all(bind=engine)

# ------------------ FASTAPI APP ------------------
app = FastAPI(title="Attendance Monitoring System")

# ------------------ HOME ROUTE ------------------
@app.get("/")
def home():
    return {"message": "Welcome to the Attendance Monitoring System API"}

# ------------------ AUTH ROUTES ------------------
@app.post("/signup", response_model=dict)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password_hash=hashed_pw, class_id=user.class_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/login", response_model=dict)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}

# ------------------ CLASSROOM ROUTES ------------------
@app.get("/classrooms", response_model=List[ClassroomResponse])
def get_classrooms(db: Session = Depends(get_db)):
    classrooms = db.query(Classroom).all()
    return classrooms

# ------------------ ATTENDANCE ROUTES ------------------
@app.post("/attendance", response_model=dict)
def mark_attendance(attendance: AttendanceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    classroom = db.query(Classroom).filter(Classroom.id == attendance.classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    new_attendance = Attendance(
        student_id=current_user.id,
        classroom_id=attendance.classroom_id,
        timestamp=datetime.utcnow(),
        verified_location=attendance.verified_location,
        verified_face=attendance.verified_face
    )
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return {"message": "Attendance marked successfully", "attendance_id": new_attendance.id}

@app.get("/attendance/history", response_model=List[AttendanceCreate])
def get_attendance_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(Attendance).filter(Attendance.student_id == current_user.id).all()
    return records

# ------------------ FOCUS MODE ROUTES ------------------
@app.post("/focus/start", response_model=dict)
def start_focus_mode(focus: FocusModeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_focus = FocusMode(
        student_id=current_user.id,
        start_time=datetime.utcnow(),
        active_status=True
    )
    db.add(new_focus)
    db.commit()
    db.refresh(new_focus)
    return {"message": "Focus Mode started", "focus_id": new_focus.id}

@app.post("/focus/stop", response_model=dict)
def stop_focus_mode(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    focus = db.query(FocusMode).filter(FocusMode.student_id == current_user.id, FocusMode.active_status == True).first()
    if not focus:
        raise HTTPException(status_code=404, detail="No active Focus Mode found")
    focus.end_time = datetime.utcnow()
    focus.active_status = False
    db.commit()
    db.refresh(focus)
    return {"message": "Focus Mode stopped"}

@app.get("/focus/status", response_model=dict)
def focus_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    focus = db.query(FocusMode).filter(FocusMode.student_id == current_user.id, FocusMode.active_status == True).first()
    if not focus:
        return {"active": False}
    return {"active": True, "start_time": focus.start_time}
