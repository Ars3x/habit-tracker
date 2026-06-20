from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional
from typing import Dict

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
    created_at: datetime 

    class Config:
        from_attributes = True
        
class PushSubscriptionCreate(BaseModel):
    endpoint: str
    keys: Dict[str, str]
    
class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    reminder_time: Optional[time] = None
    days_of_week: Optional[str] = None
    notifications_enabled: Optional[bool] = None