from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, database, auth
from pydantic import BaseModel
from datetime import timedelta, date
from .schemas import HabitCreate, HabitResponse
from .models import Habit, User
from .auth import get_current_user
from .database import get_db
from .models import HabitCompletion

app = FastAPI(title='Habit Tracker API')

class UserCreate(BaseModel):
    email: str
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/")
def root():
    return {"message": "Привет, трекер привычек!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created successfully"}

@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub":db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/habits", response_model=HabitResponse, status_code=201)
def create_habit(
    habit: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_habit = Habit(
        user_id=current_user.id,
        name=habit.name,
        description=habit.description,
        reminder_time=habit.reminder_time,
        days_of_week=habit.days_of_week
    )
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@app.get("/habits", response_model=list[HabitResponse])
def get_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    return habits

@app.post("/habits/{habit_id}/complete")
def complete_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    today = date.today()
   
    completion = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.date == today
    ).first()
    
    if completion and completion.completed:
        return {"msg": "Habit already completed today"}
    
    
    points = 5
    
    if not completion:
        completion = HabitCompletion(habit_id=habit_id, date=today, completed=True, points_earned=points)
        db.add(completion)
    else:
        completion.completed = True
        completion.points_earned = points
    
    
    current_user.total_points = (current_user.total_points or 0) + points
    
    new_level = current_user.total_points // 100 + 1
    if new_level > current_user.level:
        current_user.level = new_level
        level_up_msg = f" Поздравляем! Вы достигли {new_level} уровня!"
    else:
        level_up_msg = ""
    
    db.commit()
    return {"msg": f"Completed! +{points} points.{level_up_msg}"}