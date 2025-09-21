# app/api/routes_todo.py
"""
ルーター（routes_*.py）は 「特定の機能単位の API エンドポイント」
をまとめたファイル
"""
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.todo import TodoCreate, TodoOut, TodoUpdate
from app.services.todo_service import TodoService
from app.services.schdule_service import ScheduleService, RAGComponent
from app.database import get_db, get_vector_db
import logging
from sqlalchemy.orm import Session
from chromadb import Client




logger = logging.getLogger("uvicorn")  # uvicorn ログと統合される
logger.setLevel(logging.DEBUG)


router = APIRouter()
todo_service = TodoService()
db = next(get_db())  # SQLAlchemy Session を取得


# response_model は FastAPI がレスポンスの
# 「型・構造」を明示するための仕組み です。



# @router.post("/optimize_schedule", response_model=list[TodoOut],)
# def optimize_schedule(db: Session = Depends(get_db), rag_component: Client = Depends(get_vector_db)):
#     logger.info("Optimize schedule called")
#     optimization_service = ScheduleService(db, rag_component=rag_component)
#     logger.info("DBを引っ張ってきた。")
#     result = optimization_service.optimize_schedule()
#     logger.info(f"最適化完了")
#     return result


@router.get("/", response_model=list[TodoOut])
def get_todos(db: Session = Depends(get_db)):
    # db をサービスに渡す
    return todo_service.get_all_todos(db)


@router.post("/", response_model=TodoOut)
def create_todo(todo: TodoCreate):
    print(f"Creating todo: {todo}")
    return todo_service.create_todo(db, todo)


@router.put("/{todo_id}", response_model=TodoOut)
def update_todo(
        todo_id: int, 
        todo_update: TodoUpdate, 
        db: Session = Depends(get_db)):
    
    logger.info(f"Received update for Todo {todo_id}: {todo_update}")
    try:
        return todo_service.update_todo(db, todo_id, todo_update)
    except ValueError:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/{id}")
def delete_todo(id: int, db: Session = Depends(get_db)):
    success = todo_service.delete_todo(db, id)  # DB処理はサービスに丸投げ
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {
        "deleted": True,
        "message": "Todo deleted successfully",
        "id": id
    }
