# routes_schedule.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.todo import TodoCreate, TodoOut, TodoUpdate
from app.services.todo_service import TodoService
from app.database import get_db
from app.models.todo_model import TodoModel
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()
todo_service = TodoService()

@router.post("/optimize", response_model=List[TodoOut])
async def optimize_schedule(date: dict, db: Session = Depends(get_db)):
    try:
        # 未完了のTodoを取得
        todos = todo_service.get_all_todos(db)
        incomplete_todos = [todo for todo in todos if not todo.done]
        
        # ここで最適化ロジックを実装
        # とりあえず期限順にソート
        sorted_todos = sorted(incomplete_todos, key=lambda x: x.time_limit if x.time_limit else datetime.max)
        
        return sorted_todos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

