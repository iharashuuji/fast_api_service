# backend/app/models/todo_model.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship
import datetime



class TodoModel(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    time_limit = Column(DateTime, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    is_vectorized = Column(Boolean, default=False, nullable=False)
    suggestion_reason = Column(String, nullable=True)
    file_contents_cache = Column(JSON, nullable=True)
    llm_response_cache = Column(Text, nullable=True)
    optimization_id = Column(Integer, ForeignKey("schedule_optimization_results.id"), nullable=True)
    # このTodoが属する最適化結果を取得するためのrelationship
    optimization_result = relationship("ScheduleOptimizationResult", back_populates="todos")    

class ScheduleOptimizationResult(Base):
    __tablename__ = "schedule_optimization_results"
    # ★ 自身の独立した主キーを定義
    id = Column(Integer, primary_key=True, index=True)
    suggestion_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # この最適化結果に紐づくTodoのリストを取得するためのrelationship
    todos = relationship("TodoModel", back_populates="optimization_result")
