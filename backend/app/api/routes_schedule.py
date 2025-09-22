# routes_schedule.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.todo import TodoOut, ScheduleOptimizationResponse, ErrorResponse
from app.services.todo_service import TodoService
from app.database import get_db, get_vector_db
from typing import List, Union
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from app.services.schdule_service import ScheduleService, RAGComponent
import logging
from chromadb import Client
from chromadb.config import Settings
import google.generativeai as genai
from dotenv import load_dotenv
import os
from langchain.output_parsers import PydanticOutputParser


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
router = APIRouter()
todo_service = TodoService()
class OptimizeRequest(BaseModel):
    date: str
    

@router.get("/{task_id}/related_file")
def get_related_file(
    task_id: int, 
    db: Session = Depends(get_db),
    vector_db_client: Client = Depends(get_vector_db) 
):
    service = ScheduleService(db=db, rag_component=vector_db_client)
    file_data = service.find_related_file_for_task(task_id=task_id)
    if not file_data:
        # It's better to raise an HTTPException for proper error responses.
        raise HTTPException(status_code=404, detail="Related file not found.")
        
    return file_data


@router.post("/optimize", response_model=Union[ScheduleOptimizationResponse, ErrorResponse])
async def optimize_schedule(
    request: OptimizeRequest, 
    db: Session = Depends(get_db),
    vector_db_client: Client = Depends(get_vector_db) 
):
    logger.debug("optimize_schedule endpoint called with request: %s", request)
    try:
        # 未完了のTodoを取得
        logger.debug("Initializing TodoService")
        todos = todo_service.get_all_todos(db)
        logger.debug('Todo取得完了')
        incomplete_todos = [todo for todo in todos if not todo.done]

        # ここで最適化ロジックを実装
        # とりあえず期限順にソート
        logger.debug('ソートを開始')
        sorted_todos = sorted(
            incomplete_todos,
            key=lambda x: x.time_limit if x.time_limit else datetime.max,
        )
        # ここから、RAGを用いた、最適化処理を実行
        # ベクトル化のための設定
        # ここはGEMINIモデルを使用する。
        logger.info('モデルの呼び出し開始')
        genai.configure(api_key=api_key)
        embedding_model = genai.embed_content
        logger.info('モデルの呼び出し完了')
        # vector_client = Client(Settings(
        #     persist_directory="./vector_db"
        # ))
        # logger.info('モデルの呼び出し完了')
        rag = RAGComponent(
            embedding_model=embedding_model,
            db_session=db,
            vector_client=vector_db_client
        )
        logger.info('ベクトル化開始')
        rag.sync_sql_to_vector_db()
        logger.debug('ベクトル化完了')      
        # ここから最適化処理を行う
        
        schdule_service = ScheduleService(db=db, rag_component=vector_db_client)
        logger.info('モデルの初期化完了 & 最適化開始')
        optimized_tasks = schdule_service.optimize_schedule()
        logger.debug(f'type. optimizer_tasks{type(optimized_tasks)}')
        logger.debug(f'データをすべて取得: {optimized_tasks}')
        optimized_todos = todo_service.get_all_todos(db)
        logger.info('完了')
        
        return optimized_tasks # optimized_todos
    
    except Exception as e:
        logger.error(f"APIエンドポイントで予期せぬエラーが発生しました: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
