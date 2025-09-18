# backend/app/models/todo_model.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base
from datetime import datetime


class TodoModel(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    time_limit = Column(DateTime, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)