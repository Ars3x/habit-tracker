from sqlalchemy import Column, Integer, String, DateTime, Boolean, Time, ForeignKey
from .database import Base
import datetime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    reminder_time = Column(Time, nullable=True)
    days_of_week = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    