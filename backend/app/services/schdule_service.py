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
from sqlalchemy.orm import Session
from app.models.todo_model import TodoModel
from app.schemas.todo import TodoOut
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv

# .env ファイルをロード
load_dotenv()


# 環境変数から取得
SEARCH_DIR = os.getenv("SEARCH_DIR")  # ここを適切なディレクトリに変更
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
my_llm_instance = LLMChain(
    llm=llm, 
    prompt=PromptTemplate(
        input_variables=["text"], 
        template="{text}")
)


class ScheduleService:
    def optimize_schedule(self, db: Session, date: str):
        # tasks = db.query(TodoModel).filter(TodoModel.done == False).all()
        tasks = db.query(TodoModel).filter(TodoModel.done.is_(False)).all()

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

        # LLMに渡す
        prompt_text = (
            f"今日の日付は {date} です。\n"
            f"以下のタスクを優先度順に JSON 形式で返してください:\n"
            f"{task_list}"
        )
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


   
    def find_related_file_for_task(task_id: int, db: Session):
        """
        指定されたタスクIDに関連するファイルをAIが探し、そのパスと中身を返すエージェント関数
        """
        # 1. 特定のタスクをデータベースから取得
        task = db.query(TodoModel).filter(TodoModel.id == task_id).first()
        if not task:
            return None # タスクが見つからない場合

        # 2. 検索対象のファイルリストを取得
        files = [os.path.join(root, f) for root, _, fs in os.walk("./docs") for f in fs]
        filenames = [os.path.basename(f) for f in files]

        # 3. LLMにファイルを選ばせる (プロンプトを改善)
        prompt = f"""
        以下のファイルリストの中から、
        タスク「{task.title}」（詳細：{task.description}）
        に最も関連するファイル名を一つだけ選んで、ファイル名だけを答えてください。

        ファイルリスト: {filenames}
        """
        # 4. LLMを一度だけ実行
        selected_filename = llm.run(prompt).strip()

        # 5. 選ばれたファイルを探して中身を読み込む (より頑健な方法)
        for file_path in files:
            if selected_filename in file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 6. ファイルのパスと中身を辞書で返す
                return {"path": file_path, "content": content}

        return None # 関連ファイルが見つからない場合