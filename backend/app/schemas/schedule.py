"""
Schemas フォルダは FastAPI における
「データの型や構造」を定義する場所

「API のリクエストやレスポンスで扱う
Pydantic モデル」をまとめるフォルダ
"""

# app/schemas/todo.py
from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    title: str


class ScheduleOut(ScheduleCreate):
    id: int  # DB に保存された ID を含める
