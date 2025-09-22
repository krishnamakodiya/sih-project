from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  # your SQLAlchemy Base

# ------------------ USER TABLE ------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classrooms.id"))

    # Relationships
    attendance = relationship("Attendance", back_populates="student")
    focus_modes = relationship("FocusMode", back_populates="student")
    classroom = relationship("Classroom", back_populates="students")


# ------------------ CLASSROOM TABLE ------------------
class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    static_qr_code = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=True)

    # Relationships
    students = relationship("User", back_populates="classroom")
    attendance_records = relationship("Attendance", back_populates="classroom")


# ------------------ ATTENDANCE TABLE ------------------
class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    verified_location = Column(Boolean, default=False)
    verified_face = Column(Boolean, default=False)

    # Relationships
    student = relationship("User", back_populates="attendance")
    classroom = relationship("Classroom", back_populates="attendance_records")


# ------------------ FOCUS MODE TABLE ------------------
class FocusMode(Base):
    __tablename__ = "focus_modes"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    active_status = Column(Boolean, default=True)

    # Relationships
    student = relationship("User", back_populates="focus_modes")
