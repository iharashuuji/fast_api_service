"""
ルーター（routes_*.py）は 「特定の機能単位の API エンドポイント」
をまとめたファイル
"""

# app/api/routes_todo.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.todo import TodoCreate, TodoOut
from app.services.todo_service import TodoService
from app.database import get_db
from app.models.todo_model import TodoModel


router = APIRouter()
todo_service = TodoService()
db = next(get_db())  # SQLAlchemy Session を取得

# response_model は FastAPI がレスポンスの
# 「型・構造」を明示するための仕組み です。
from sqlalchemy.orm import Session

@router.get("/", response_model=list[TodoOut])
def get_todos(db: Session = Depends(get_db)):
    
    # db をサービスに渡す
    return todo_service.get_all_todos(db)

@router.post("/", response_model=TodoOut)
def create_todo(todo: TodoCreate):
    print(f'Creating todo: {todo}')
    return todo_service.create_todo(db, todo)

@router.put("/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo: TodoCreate):
    try:
        return todo_service.update_todo(todo_id, todo)
    except ValueError:
        raise HTTPException(status_code=404, detail="Todo not found")

# @router.delete("/{todo_id}")
# def delete_todo(todo_id: int):
#     success = todo_service.delete_todo(todo_id)
#     return {"deleted": success}

@router.delete("/{id}")
def delete_todo(id: int):
    todo = db.query(TodoModel).filter(TodoModel.id == id).first()
    db.delete(todo)
    db.commit()
    return {"deleted": True, "message": "Todo deleted successfully", "id": id}
