from pydantic import BaseModel, EmailStr
from typing import Optional

# ------------------ USER SCHEMAS ------------------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    class_id: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ------------------ CLASSROOM SCHEMA ------------------

class ClassroomResponse(BaseModel):
    id: int
    name: str
    static_qr_code: str
    location: Optional[str]

    class Config:
        orm_mode = True

# ------------------ ATTENDANCE SCHEMA ------------------

class AttendanceCreate(BaseModel):
    classroom_id: int
    verified_location: Optional[bool] = False
    verified_face: Optional[bool] = False

    class Config:
        orm_mode = True

# ------------------ FOCUS MODE SCHEMA ------------------

class FocusModeCreate(BaseModel):
    # If needed, you can add extra fields like planned duration
    pass
