# app/api/routes_todo.py
"""
ルーター（routes_*.py）は 「特定の機能単位の API エンドポイント」
をまとめたファイル
"""
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.todo import TodoCreate, TodoOut, TodoUpdate
from app.services.todo_service import TodoService
from app.services.schdule_service import ScheduleService
from app.database import get_db
from app.models.todo_model import TodoModel
import logging
from typing import List
from sqlalchemy.orm import Session


logger = logging.getLogger("uvicorn")  # uvicorn ログと統合される
logger.setLevel(logging.DEBUG)

router = APIRouter()
todo_service = TodoService()
db = next(get_db())  # SQLAlchemy Session を取得

# response_model は FastAPI がレスポンスの
# 「型・構造」を明示するための仕組み です。
optimization_service = ScheduleService()

@router.post("/optimize_schedule", response_model=list[TodoOut])
def optimize_schedule(db: Session = Depends(get_db)):
    result = optimization_service.optimize_schedule(db)
    return result

@router.get("/", response_model=list[TodoOut])
def get_todos(db: Session = Depends(get_db)):
    
    # db をサービスに渡す
    return todo_service.get_all_todos(db)

@router.post("/", response_model=TodoOut)
def create_todo(todo: TodoCreate):
    print(f'Creating todo: {todo}')
    return todo_service.create_todo(db, todo)

@router.put("/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    logger.info(f"Received update for Todo {todo_id}: {todo_update}")
    try:
        return todo_service.update_todo(db, todo_id, todo_update)
    except ValueError:
        raise HTTPException(status_code=404, detail="Todo not found")

# @router.delete("/{id}")
# def delete_todo(id: int):
#     todo = db.query(TodoModel).filter(TodoModel.id == id).first()
#     db.delete(todo)
#     db.commit()
#     return {"deleted": True, "message": "Todo deleted successfully", "id": id}
@router.delete("/{id}")
def delete_todo(id: int, db: Session = Depends(get_db)):
    success = todo_service.delete_todo(db, id)  # ← DB処理はサービスに丸投げ
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"deleted": True, "message": "Todo deleted successfully", "id": id}
