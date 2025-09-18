"""
Schemas フォルダは FastAPI における
「データの型や構造」を定義する場所

「API のリクエストやレスポンスで扱う
Pydantic モデル」をまとめるフォルダ
"""

# app/schemas/todo.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    done: bool = False
    time_limit: Optional[datetime] = None
    estimated_minutes: Optional[int] = None

class TodoOut(TodoCreate):
    id: int  # DB に保存された ID を含める

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None
    time_limit: Optional[datetime] = None
    estimated_minutes: Optional[int] = None