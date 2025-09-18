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
from langchain import LLMChain, PromptTemplate
from fastapi import FastAPI
from typing import List
from app.schemas.todo import TodoCreate, TodoOut
from app.schemas.schedule import ScheduleCreate, ScheduleOut
from sqlalchemy.orm import Session
from app.models.todo_model import TodoModel
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# .env ファイルをロード
load_dotenv()

# 環境変数から取得
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
my_llm_instance = LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["text"], template="{text}"))


# LLMのプロンプトをだして、DBから取得したデータを渡す。
# class ScheduleService:
#     def optimize_schedule(self, db: Session, date: str):
#         # DBからタスクを取得
#         tasks = db.query(TodoModel).all()
#         task_list = [{"id": t.id, "title": t.title, "done": t.done, "priority": t.priority, "estimated": t.estimated_minutes, "time": t.time_limit} for t in tasks]

#         # DBのDoneカラムがFalseであるものだけを返すように処理をする
#         if task_list['done'] == True:
#             task_list.remove(task_list['done'])
#         else:
#             pass
#         # LLMに渡す
#         prompt_text = f"""
#         今日の日付は {date} です。
#         以下のタスクを優先度順に JSON 形式で返してください:
#         {task_list}
#         """
#         result = my_llm_instance.run(prompt_text)
#         optimized_tasks = json.loads(result)

#         # 優先度カラムに反映
#         for idx, task_info in enumerate(optimized_tasks):
#             todo = db.query(TodoModel).filter(TodoModel.id == task_info["id"]).first()
#             if todo:
#                 todo.priority = idx
#         db.commit()
#         return optimized_tasks

class ScheduleService:
    def optimize_schedule(self, db: Session, date: str):
        tasks = db.query(TodoModel).filter(TodoModel.done == False).all()
        task_list = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "done": t.done,
                "priority": t.priority,
                "estimated_minutes": t.estimated_minutes,
                "time_limit": t.time_limit.isoformat() if t.time_limit else None,
            }
            for t in tasks
        ]

        prompt_text = f"""
        今日の日付は {date} です。
        以下のタスクを優先度順に JSON 形式で返してください:
        {json.dumps(task_list, ensure_ascii=False)}
        """
        result = my_llm_instance.run(prompt_text)
        optimized_tasks = json.loads(result)

        # DBに優先度を反映
        for idx, task_info in enumerate(optimized_tasks):
            todo = db.query(TodoModel).filter(TodoModel.id == task_info["id"]).first()
            if todo:
                todo.priority = idx
        db.commit()

        # 🔥 TodoOut に変換して返す
        return [
            TodoOut(
                id=task["id"],
                title=task["title"],
                description=task.get("description"),
                done=task["done"],
                priority=task.get("priority"),
                estimated_minutes=task.get("estimated_minutes"),
                time_limit=task.get("time_limit"),
            )
            for task in optimized_tasks
        ]