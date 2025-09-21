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
from chromadb import Client
import logging
from pydantic import BaseModel, Field
from typing import List
from langchain.output_parsers import PydanticOutputParser


class OptimizedTaskUpdate(BaseModel):
    id: int = Field(description="更新対象のタスクID")
    priority: int = Field(description="提案する新しい優先順位（0から始まる連番）")
    reason: str = Field(description="なぜこの優先順位になったかの簡潔な理由")

class ScheduleUpdateOutput(BaseModel):
    schedule_updates: List[OptimizedTaskUpdate] = Field(description="タスクの更新情報のリスト")

load_dotenv()

# 環境変数から設定をロードし、ブール値として変換
use_local_api = os.getenv("USE_LOCAL_API") == "true"
lmstudio_model_name = os.getenv('LOCAL_MODEL_NAME')
use_local_embedding = os.getenv("USE_LOCAL_EMBEDDING") == "true"
google_api_key = os.getenv("GOOGLE_API_KEY")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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
        temperature=0.3,
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
# class RAGComponent:
#     def __init__(self, embedding_model, db_session: Session):
#         self.embedding_model = embedding_model
#         self.db_session = db_session
#         print("RAGComponent: ベクトルデータベースの準備中...")
#         # ここにベクトルデータベースのインスタンスを初期化します (例: self.vector_db = ChromaDB(...))

#     def create_vector_for_text(self, text: str) -> list:
#         """DB内のDesctiprtionとTitle、日付、完了済みかどうかをベクトル化する"""
#         vector_item = self.db_session.query(TodoModel)
#         if not self.embedding_model:
#             print("Embedding model is not available.")
#             return []
#         # ベクトル化する情報を一つの文字列にまとめる
#         # time_limitがNoneの場合も考慮
#         time_limit_str = task.time_limit.isoformat() if task.time_limit else "期限なし"
        
#         text_to_embed = (
#             f"タスク名: {task.title}\n"
#             f"詳細: {task.description}\n"
#             f"期限: {time_limit_str}\n"
#             f"見積時間(分): {task.estimated_minutes}\n"
#             f"完了済み: {'はい' if task.done else 'いいえ'}"
#         )

# # --- RAG Component: RAGのロジックをカプセル化 ---
# class RAGComponent:
#     def __init__(self, embedding_model, db_session: Session):
#         self.embedding_model = embedding_model
#         self.db_session = db_session
#         print("RAGComponent: ベクトルデータベースの準備中...")
#         # ここにベクトルデータベースのインスタンスを初期化します (例: self.vector_db = ChromaDB(...))

#     def _create_vector_from_task(self, task: TodoModel) -> list:
#         """TodoModelオブジェクトからベクトルを生成する内部メソッド"""
#         if not self.embedding_model:
#             print("Embedding model is not available.")
#             return []

#         # ベクトル化する情報を一つの文字列にまとめる
#         # time_limitがNoneの場合も考慮
#         time_limit_str = task.time_limit.isoformat() if task.time_limit else "期限なし"
        
#         text_to_embed = (
#             f"タスク名: {task.title}\n"
#             f"詳細: {task.description}\n"
#             f"期限: {time_limit_str}\n"
#             f"見積時間(分): {task.estimated_minutes}\n"
#             f"完了済み: {'はい' if task.done else 'いいえ'}"
#         )
        
#         print(f"Embedding a following text:\n---\n{text_to_embed}\n---")

#         try:
#             if use_local_embedding:
#                 # LM Studioモデルの呼び出し方を調整
#                 return self.embedding_model.embed(text_to_embed)
#             else:
#                 # Google AIのembeddingモデルを使用
#                 return self.embedding_model(model="models/embedding-001", content=text_to_embed)['embedding']
#         except Exception as e:
#             print(f"An error occurred during vectorization for task ID {task.id}: {e}")
#             return []
        

#     def index_tasks_for_rag(self):
#         """DBから全てのタスクを取得し、ベクトル化してインデックスに登録する"""
#         print("RAGComponent: DBからタスクを取得し、インデックスを作成中...")
        
#         # DBからすべてのタスクを取得
#         tasks_to_index = self.db_session.query(TodoModel).all()
        
#         if not tasks_to_index:
#             print("インデックス対象のタスクが見つかりません。")
#             return

#         for task in tasks_to_index:
#             vector = self._create_vector_from_task(task)
#             if vector:
#                 # ここでベクトルとメタデータをベクトルデータベースに格納
#                 # 例: self.vector_db.add_document(vector, {"id": task.id, "title": task.title})
#                 print(f"タスク '{task.title}' (ID: {task.id}) をインデックス化しました。")
                
                
#     def find_relevant_tasks_with_rag(self, query: str, num_results=5) -> list[TodoModel]:
#         """クエリに基づいて関連タスクを検索 (推論・フェーズ)"""
#         print(f"RAGComponent: クエリ '{query}' に基づいて関連タスクを検索中...")
#         query_vector = self.create_vector_for_text(query)
        
#         # 実際にはここでベクトル検索を実行
#         # relevant_ids = self.vector_db.search(query_vector, k=num_results)
#         # relevant_tasks = self.db_session.query(TodoModel).filter(TodoModel.id.in_(relevant_ids)).all()
#         # 仮の実装として、未完了タスクの中から関連タスクを抽出
#         unfinished_tasks = self.db_session.query(TodoModel).filter(TodoModel.done.is_(False)).all()
#         return unfinished_tasks[:num_results]


# schdule_service.py の RAGComponent クラス内

# --- RAG Component: RAGのロジックをカプセル化 ---
class RAGComponent:
    def __init__(self, embedding_model, db_session: Session, vector_client: Client):
        self.embedding_model = embedding_model
        self.db_session = db_session
        self.vector_client = vector_client  # ChromaDBクライアントを受け取る
        print("RAGComponent: 初期化完了。")
        # "tasks"という名前のコレクション（テーブルのようなもの）を取得または新規作成
        self.collection = self.vector_client.get_or_create_collection(name="tasks")

    def _create_text_from_task(self, task: TodoModel) -> str:
        """TodoModelオブジェクトからベクトル化するための単一のテキストを生成する"""
        time_limit_str = task.time_limit.isoformat() if task.time_limit else "期限なし"
        return (
            f"タスク名: {task.title}\n"
            f"詳細: {task.description}\n"
            f"期限: {time_limit_str}\n"
            f"完了済み: {'はい' if task.done else 'いいえ'}"
        )

    def sync_sql_to_vector_db(self):
        """
        SQLデータベースのタスクをベクトル化し、ChromaDBに同期（保存）する。
        アプリケーション起動時や、データ更新時に呼び出すことを想定。
        """
        print("RAGComponent: SQL DBからベクトルDBへの同期を開始します...")

        # 1. SQL DBから全タスクを取得
        tasks_to_sync = self.db_session.query(TodoModel).filter(
            TodoModel.is_vectorized == False
        ).all()
        
        if not tasks_to_sync:
            print("同期対象のタスクがSQL DBに存在しません。")
            return

        # ChromaDBに一括登録するためのリストを準備
        embeddings = []
        metadatas = []
        ids = []

        # 2. 各タスクをループしてベクトル化
        for task in tasks_to_sync:
            # 2-1. タスク情報を1つのテキストにまとめる
            text_to_embed = self._create_text_from_task(task)

            # 2-2. テキストをベクトルに変換
            try:
                if use_local_embedding:
                    vector = self.embedding_model.embed(text_to_embed)
                else:
                    vector = self.embedding_model(model="models/embedding-001", content=text_to_embed)['embedding']
                
                embeddings.append(vector)
                
                # 2-3. メタデータを作成 (SQLのIDやタイトルを格納)
                metadatas.append({
                    "sql_id": task.id,
                    "title": task.title,
                    "done": task.done
                })
                
                # 2-4. ChromaDB内で一意となるIDを作成 (SQLのIDを文字列として使うのが簡単)
                ids.append(str(task.id))

            except Exception as e:
                print(f"タスクID {task.id} のベクトル化中にエラーが発生しました: {e}")

        # 3. 準備したリストをChromaDBに一括で追加 (upsert=Trueで既存IDは更新)
        if ids:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"{len(ids)}件のタスクをベクトルDBに同期しました。")
        # 4. ★★★【重要】処理したタスクのフラグを 'True' に更新★★★
        for task in tasks_to_sync:
            task.is_vectorized = True
        
        # 5. ★★★データベースの変更を確定★★★
        self.db_session.commit()
        print("SQL DBのベクトル化フラグを更新しました。")

    def find_relevant_tasks_with_rag(self, query: str, num_results=5) -> list:
        """クエリに基づいて関連タスクをベクトル検索する"""
        print(f"RAGComponent: クエリ '{query}' に基づいて関連タスクを検索中...")
        
        # クエリをベクトル化
        if use_local_embedding:
            query_vector = self.embedding_model.embed(query)
        else:
            query_vector = self.embedding_model(model="models/embedding-001", content=query)['embedding']

        # ChromaDBで類似ベクトルを検索
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=num_results
        )
        
        # 検索結果からメタデータを返す（実際のタスク情報はここからSQL IDで引く）
        return results['metadatas'][0] if results['metadatas'] else []
    

# --- Service Class ---
# class ScheduleService:
    # def __init__(self, db: Session, rag_component: RAGComponent):
    #     # __init__ はこのままでOK！依存性を明確に受け取る良い設計です。
    #     self.db = db
    #     self.rag = rag_component
    #     self.llm_chain = LLMChain(
    #         llm=llm,
    #         prompt=PromptTemplate(
    #             input_variables=["context", "query"],
    #             template="コンテキスト: {context}\n\nタスク: {query}\n\nこの情報を使って、具体的で最適なスケジュールを提案してください。"
    #         )
    #     )
class ScheduleService:
    def __init__(self, db: Session, rag_component: RAGComponent):
        self.db = db
        self.rag = rag_component
        self.parser = PydanticOutputParser(pydantic_object=ScheduleUpdateOutput)
        self.prompt = PromptTemplate(
            template=(
                "以下のタスクリストを最も効率的な実行順序に並び替え、各タスクのID、新しい優先順位(priority)、その順序にした理由(reason)をJSON形式で返してください。\n"
                "{format_instructions}\n"
                "タスクリスト:\n{context}\n"
            ),
            input_variables=["context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.llm_chain = LLMChain(llm=llm, prompt=self.prompt)

    # def optimize_schedule(self, query: str):
    #     """RAGを使ってスケジュールを最適化する"""
        
    #     # 1. RAGコンポーネントで関連タスクの「メタデータ」を取得
    #     # (find_relevant_tasks_with_ragはIDやタイトルを含む辞書のリストを返します)
    #     relevant_task_metadatas = self.rag.find_relevant_tasks_with_rag(query)
    #     if not relevant_task_metadatas:
    #         return "関連するタスクが見つかりませんでした。"

    #     # 2. ★★★【重要】メタデータからSQLのIDを抽出し、DBから完全なタスク情報を取得★★★
    #     relevant_task_ids = [meta['sql_id'] for meta in relevant_task_metadatas]
        
    #     # SQLAlchemyの .in_() を使って、IDリストに一致するタスクを一度のクエリで取得
    #     full_relevant_tasks = self.db.query(TodoModel).filter(TodoModel.id.in_(relevant_task_ids)).all()

    #     # 3. 取得したタスク情報をプロンプトのコンテキストにまとめる
    #     # (これで t.description など全てのプロパティに安全にアクセスできます)
    #     context_docs = [
    #         Document(page_content=f"タスク: {t.title} - 詳細: {t.description} (完了: {t.done})") 
    #         for t in full_relevant_tasks
    #     ]
        
    #     # 4. LLMに最適化を依頼 (ここは変更なし)
    #     result = self.llm_chain.invoke({
    #         "context": context_docs,
    #         "query": query
    #     })
        
    #     # 5. LLMの応答を解析して返す (簡略化)
    #     try:
    #         # 本来はここでLLMからのJSONレスポンスを解析し、DB更新などを行う
    #         # optimized_tasks_info = json.loads(result['text'])
    #         return result['text'] # LLMの生の応答を一旦返す
    #     except json.JSONDecodeError:
    #         return "LLMからの応答形式が不正です。"
    #     except Exception as e:
    #         return f"エラーが発生しました: {e}"
    
    
    def optimize_schedule(self):
        """全ての未完了タスクを対象にスケジュールを最適化する"""
    
        # 1. 未完了タスクを直接取得
        logger.info('タスクの取得')
        incomplete_tasks = self.db.query(TodoModel).filter(
            TodoModel.done == False
        ).all()

        if not incomplete_tasks:
            return "最適化対象のタスクが見つかりませんでした。"

        # 2. タスク情報をコンテキストにまとめる
        context_docs = [
            Document(page_content=(
            f"タスク: {t.title}\n"
            f"詳細: {t.description}\n"
            f"期限: {t.time_limit}\n"
            f"見積時間: {t.estimated_minutes}分"
            )) 
            for t in incomplete_tasks
        ]
    
        # 3. LLMに最適化を依頼
        result = self.llm_chain.invoke({
            "context": context_docs,
            "query": "これらのタスクの最適な実行順序とスケジュールを提案してください。期限と見積時間を考慮してください。"
        })
        
        try:
            return result['text']
        except Exception as e:
            return f"スケジュール最適化中にエラーが発生しました: {e}"

        except Exception as e:
            logger.error(f"スケジュール最適化中にエラーが発生: {e}")
            # エラー時は元の未完了タスクをそのまま返す
            return self.db.query(TodoModel).filter(TodoModel.done == False).all()


    def find_related_file_for_task(self, task_id: int):
        """
        指定されたタスクIDに関連するファイルを探す（このメソッドのロジックはOK）
        """
        # self.db を使ってDBセッションにアクセスできているので、この実装は正しいです。
        task = self.db.query(TodoModel).filter(TodoModel.id == task_id).first()
        if not task:
            return None
        
        # ToDo: ファイル検索のRAGロジックをここに実装する
        print(f"ID: {task_id} ({task.title}) に関連するファイルを検索します...")
        return {"file_found": "True", "content": "関連ファイルの内容（仮）"}
    