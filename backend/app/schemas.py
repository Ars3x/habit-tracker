from pydantic import BaseModel
from datetime import time
from typing import Optional

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    reminder_time: Optional[time] = None
    days_of_week: Optional[str] = None
    
class HabitResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    reminder_time: Optional[time]
    days_of_week: Optional[str]
    created_at: str 

    class Config:
        from_attributes = True