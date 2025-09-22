# backend/app/models/todo_model.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from app.database import Base


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
    