# routes_schedule.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.todo import TodoOut
from app.services.todo_service import TodoService
from app.database import get_db, get_vector_db
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from app.services.schdule_service import ScheduleService
import logging

router = APIRouter()
todo_service = TodoService()
class OptimizeRequest(BaseModel):
    date: str
    

@router.get("/{task_id}/related_file")
def get_related_file(
    task_id: int, 
    db: Session = Depends(get_db),
    rag_component = Depends(get_vector_db) 
):
    service = ScheduleService(db=db, rag_component=rag_component)
    file_data = service.find_related_file_for_task(task_id=task_id)
    if not file_data:
        # It's better to raise an HTTPException for proper error responses.
        raise HTTPException(status_code=404, detail="Related file not found.")
        
    return file_data


@router.post("/optimize", response_model=List[TodoOut])
async def optimize_schedule(
    request: OptimizeRequest, 
        db: Session = Depends(get_db)):
    try:
        # 未完了のTodoを取得
        todos = todo_service.get_all_todos(db)
        logging.info('Todo取得完了')
        incomplete_todos = [todo for todo in todos if not todo.done]

        # ここで最適化ロジックを実装
        # とりあえず期限順にソート
        logging.info('ソートを開始')
        sorted_todos = sorted(
            incomplete_todos,
            key=lambda x: x.time_limit if x.time_limit else datetime.max,
        )
        # ここから、RAGを用いた、最適化処理を実行
        # TodoOutの形式に変換して返す
        return [
            TodoOut(
                id=todo.id,
                title=todo.title,
                done=todo.done,
                time_limit=todo.time_limit,
                estimated_minutes=todo.estimated_minutes,
            )
            for todo in sorted_todos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
