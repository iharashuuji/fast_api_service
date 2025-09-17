"""
LLMに推論をさせて、スケジュールの最適化を行う
必要なものは、Openai apiと、スケジュールを取得する事、そのスケジュールとその人がどれくらいのタスクをうまくさばけるかを考える。
ただ、スケジュールの最適化って、難しいかなと思うが、開いている時間でちょっとした課題とかはやればいいが、テスト勉強！とか時間をまとめて取った方がいいやつとかはかなりいいかなと思っている、
そこで、スケジュールの中で、動くスケジュールと、固定して決めるべきスケジュールを考えるべきかなと思った。このあたりの数値の調節は自分自身でやってもらう方がいいかなと思う

    作成機能 TodoCreate
    title: str
    description: Optional[str] = None
    done: bool = False
    
    削除機能 TodoOut
    id: int  # DB に保存された ID を含める
"""



# app/services/todo_service.py
from fastapi import FastAPI
from typing import List
from app.schemas.todo import TodoCreate, TodoOut
from app.schemas.schedule import ScheduleCreate, ScheduleOut
from app.services.todo_service import fake_db as todo_db


# LLMのプロンプトをだして、DBから取得したデータを渡す。
