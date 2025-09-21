# app/services/todo_service.py

# --- Imports ---
from sqlalchemy.orm import Session
from app.models.todo_model import TodoModel
from app.schemas.todo import TodoOut
import os
import json
from datetime import datetime, timezone
import re

# --- AI & API Configuration ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

# LM Studio (Python Client) for local embedding model
import lmstudio as lms
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 環境変数から設定をロードし、ブール値として変換
use_local_api = os.getenv("USE_LOCAL_API") == "true"
lmstudio_model_name = os.getenv('LOCAL_MODEL_NAME')
use_local_embedding = os.getenv("USE_LOCAL_EMBEDDING") == "true"
google_api_key = os.getenv("GOOGLE_API_KEY")

# --- 1. LLMインスタンスの初期化 (プログラム起動時に一度だけ実行) ---
if use_local_api:
    llm = ChatOpenAI(
        model=lmstudio_model_name,
        api_key="lm-studio",
        base_url="http://localhost:1234/v1"
    )
    print("AI: LM Studioのローカルモデルを使用します。")
else:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        google_api_key=google_api_key
    )
    print("AI: Geminiモデルを使用します。")

# --- 2. Embeddingモデルの初期化 ---
if use_local_embedding:
    try:
        embedding_model = lms.embedding_model("nomic-embed-text-v1.5")
    except TypeError:
        print("LM Studio embedding model could not be loaded. Check if the model name is correct.")
        embedding_model = None
else:
    try:
        genai.configure(api_key=google_api_key)
        embedding_model = genai.embed_content
    except Exception as e:
        print(f"Gemini embedding model could not be loaded: {e}")
        embedding_model = None


# --- RAG Component: RAGのロジックをカプセル化 ---
class RAGComponent:
    def __init__(self, embedding_model, db_session: Session):
        self.embedding_model = embedding_model
        self.db_session = db_session
        print("RAGComponent: ベクトルデータベースの準備中...")
        # ここにベクトルデータベースのインスタンスを初期化します (例: self.vector_db = ChromaDB(...))

    def create_vector_for_text(self, text: str) -> list:
        """テキストをベクトル化する"""
        if not self.embedding_model:
            print("Embedding model is not available.")
            return []
        
        if use_local_embedding:
            # LM Studioモデルの呼び出し方を調整
            return self.embedding_model.embed(text)
        else:
            return self.embedding_model(model="models/embedding-001", content=text)['embedding']

    def index_tasks_for_rag(self, tasks: list[TodoModel]):
        """タスクリストをベクトル化してデータベースに格納 (インデックス・フェーズ)"""
        print("RAGComponent: タスクのインデックスを作成中...")
        for task in tasks:
            text_to_embed = f"タスク名: {task.title}\n詳細: {task.description}\n完了済み: {task.done}"
            vector = self.create_vector_for_text(text_to_embed)
            if vector:
                # ここでベクトルとメタデータをベクトルデータベースに格納
                # 例: self.vector_db.add_document(vector, {"id": task.id, "title": task.title})
                print(f"タスク '{task.title}' をインデックス化しました。")

    def find_relevant_tasks_with_rag(self, query: str, num_results=5) -> list[TodoModel]:
        """クエリに基づいて関連タスクを検索 (推論・フェーズ)"""
        print(f"RAGComponent: クエリ '{query}' に基づいて関連タスクを検索中...")
        query_vector = self.create_vector_for_text(query)
        
        # 実際にはここでベクトル検索を実行
        # relevant_ids = self.vector_db.search(query_vector, k=num_results)
        # relevant_tasks = self.db_session.query(TodoModel).filter(TodoModel.id.in_(relevant_ids)).all()
        # 仮の実装として、未完了タスクの中から関連タスクを抽出
        unfinished_tasks = self.db_session.query(TodoModel).filter(TodoModel.done.is_(False)).all()
        return unfinished_tasks[:num_results]

# --- Service Class ---
class ScheduleService:
    def __init__(self, db: Session, rag_component: RAGComponent):
        self.db = db
        self.rag = rag_component
        self.llm_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                input_variables=["context", "query"],
                template="コンテキスト: {context}\n\nタスク: {query}\n\nこの情報を使って、具体的で最適なスケジュールを提案してください。"
            )
        )


    def optimize_schedule(self, query: str):
        """RAGを使ってスケジュールを最適化する"""
        # 1. RAGコンポーネントで関連タスクを取得
        relevant_tasks = self.rag.find_relevant_tasks_with_rag(query)
        # 2. 取得したタスク情報をプロンプトのコンテキストにまとめる
        context_docs = [
            Document(page_content=f"タスク: {t.title} - {t.description} (完了: {t.done})") for t in relevant_tasks
        ]
        # 3. LLMに最適化を依頼
        result = self.llm_chain.invoke({
            "context": context_docs,
            "query": query
        })
        # 4. LLMの応答を解析してDBを更新 (簡略化)
        try:
            optimized_tasks_info = json.loads(result['text'])
            return "スケジュールが最適化されました。"
        except json.JSONDecodeError:
            return "LLMからの応答形式が不正です。"


    def find_related_file_for_task(self, task_id: int):
        """RAGを使って関連ファイルを探す"""
        task = self.db.query(TodoModel).filter(TodoModel.id == task_id).first()
        if not task:
            return None
        
        # ファイルのインデックス化が必要 (ここでは実装を省略)
        # files_indexed_by_rag = self.rag.find_relevant_documents(task.title)
        return {"file_found": "True", "content": "関連ファイルの内容"}
