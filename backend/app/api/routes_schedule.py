# routes_schedule.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.todo import TodoCreate, TodoOut, TodoUpdate
from app.services.todo_service import ScheduleService

from app.database import get_db
from app.models.todo_model import TodoModel
import logging
from typing import List
from sqlalchemy.orm import Session
from app.services.schdule_service import ScheduleService

schedule_service = ScheduleService()
router = APIRouter()  # ← これが必須
db = next(get_db())  # SQLAlchemy Session を取得


@router.get("/", response_model=list[TodoOut])
def get_todos(db: Session = Depends(get_db)):
    
    # db をサービスに渡す
    return schedule_service.get_all_todos(db)

