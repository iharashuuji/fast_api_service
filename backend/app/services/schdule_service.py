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
search_directory = os.getenv("SEARCH_DIR")

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

        # ファイル検索用のプロンプトを定義
        self.file_search_prompt = PromptTemplate(
            template=(
                "以下のタスクに関連する最適なファイルを選び、その理由を説明してください。\n\n"
                "タスク情報:\n{task_info}\n\n"
                "検索対象ファイル:\n{files}\n\n"
                "回答形式:\n"
                "選択したファイル: [ファイルパス]\n"
                "選択理由: [理由の説明]\n"
                "関連度: [高/中/低]\n"
            ),
            input_variables=["task_info", "files"]
        )
        self.chain = self.file_search_prompt | llm
    
    # def optimize_schedule(self):
    #     """全ての未完了タスクを対象にスケジュールを最適化する"""
    
    #     # 1. 未完了タスクを直接取得
    #     logger.info('タスクの取得')
    #     incomplete_tasks = self.db.query(TodoModel).filter(
    #         TodoModel.done == False
    #     ).all()

    #     if not incomplete_tasks:
    #         return "最適化対象のタスクが見つかりませんでした。"

    #     # 2. タスク情報をコンテキストにまとめる
    #     context_docs = [
    #         Document(page_content=(
    #         f"タスク: {t.title}\n"
    #         f"詳細: {t.description}\n"
    #         f"期限: {t.time_limit}\n"
    #         f"見積時間: {t.estimated_minutes}分"
    #         )) 
    #         for t in incomplete_tasks
    #     ]
    
    #     # 3. LLMに最適化を依頼
    #     result = self.llm_chain.invoke({
    #         "context": context_docs,
    #         "query": "これらのタスクの最適な実行順序とスケジュールを提案してください。期限と見積時間を考慮してください。"
    #     })
        
        
        
    #     try:
    #         return result['text']
    #     except Exception as e:
    #         return f"スケジュール最適化中にエラーが発生しました: {e}"

    #     except Exception as e:
    #         logger.error(f"スケジュール最適化中にエラーが発生: {e}")
    #         # エラー時は元の未完了タスクをそのまま返す
    #         return self.db.query(TodoModel).filter(TodoModel.done == False).all()
    def optimize_schedule(self):
        """全ての未完了タスクを対象にスケジュールを最適化し、提案としてDBに保存する"""
        
        try:
            # 1. 未完了タスクを直接取得
            logger.info('未完了タスクの取得を開始')
            incomplete_tasks = self.db.query(TodoModel).filter(
                TodoModel.done == False
            ).all()

            if not incomplete_tasks:
                # ★ 提案を作成せずにメッセージを返す
                return {"suggestion_text": "最適化対象のタスクが見つかりませんでした。"}

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
            logger.info('LLMにスケジュール最適化を依頼')
            result = self.llm_chain.invoke({
                "context": context_docs,
                "query": "これらのタスクの最適な実行順序とスケジュールを、具体的な時間や手順を含めて提案してください。期限と見積時間を考慮し、簡潔なマークダウン形式でまとめてください。"
            })
            
            # ★ 4. LLMの応答テキストを抽出
            #    (お使いのLangChainのバージョンにより .content または ['text'])
            suggestion_text = result.content if hasattr(result, 'content') else result.get('text', '')

            if not suggestion_text:
                raise ValueError("LLMから有効な応答テキストを取得できませんでした。")

            # ★ 5. 新しい提案オブジェクトを作成し、DBに保存
            logger.info('LLMの提案をデータベースに保存')
            new_suggestion = ScheduleOptimizationResult(
                suggestion_text=suggestion_text
            )
            self.db.add(new_suggestion)
            self.db.commit()
            self.db.refresh(new_suggestion) # DBに保存された最新の状態を取得

            # ★ 6. 保存した提案オブジェクトを返す
            return new_suggestion

        except Exception as e:
            logger.error(f"スケジュール最適化中にエラーが発生: {e}")
            # エラー発生時はエラー情報を含んだオブジェクトを返す
            return {"error": f"スケジュール最適化中にエラーが発生しました: {str(e)}"}



    def find_related_file_for_task(self, task_id: int):
        """指定されたタスクIDに関連するファイルを探す"""
        logger.info(f"タスクID {task_id} の関連ファイル検索を開始")

        # 1. タスク情報の取得
        task = self.db.query(TodoModel).filter(TodoModel.id == task_id).first()
        if not task:
            logger.warning(f"タスクID {task_id} が見つかりません")
            return None # エラーレスポンスを返す方が親切かもしれません

        # 2. 先にLLMの応答キャッシュを確認する
        if task.llm_response_cache:
            logger.info(f"タスクID {task_id} のLLM応答キャッシュが見つかりました。")
            # 応答キャッシュがあるなら、ファイル内容もキャッシュされているはず
            return {
                "file_found": bool(task.file_contents_cache),
                "llm_response": task.llm_response_cache,
                "raw_files": task.file_contents_cache
            }

        # 3. LLMキャッシュがない場合、次にファイル内容のキャッシュを確認
        if task.file_contents_cache:
            logger.info(f"タスクID {task_id} のファイル内容キャッシュが見つかりました。")
            file_contents = task.file_contents_cache
        else:
            logger.info(f"タスクID {task_id} のキャッシュはありません。ファイルシステムをスキャンします。")
            # 4. キャッシュがない場合、ファイルシステムをスキャン
            file_contents = []
            for root, _, files in os.walk(search_directory):
                for file in files:
                    if file.endswith(('.txt', '.md', '.py', '.js', '.html', '.css')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                file_contents.append({
                                    'path': os.path.relpath(file_path, search_directory),
                                    'content': content[:1000] # 内容を1000文字に制限
                                })
                        except Exception as e:
                            logger.warning(f"ファイル {file_path} の読み込みに失敗: {e}")

            # 5. スキャン結果をDBに保存（キャッシュする）
            if file_contents:
                task.file_contents_cache = file_contents
                self.db.commit()
                self.db.refresh(task) # DBの最新の状態でtaskオブジェクトを更新
                logger.info(f"タスクID {task_id} のファイルコンテンツをDBにキャッシュしました。")

        # ★★★ ロジックの変更はここまで ★★★

        try:
            # 6. LLMで関連性を判定 (この部分は変更なし)
            result = self.chain.invoke({
                "task_info": f"タイトル: {task.title}\n説明: {task.description}\n期限: {task.time_limit}\n",
                "files": "\n".join([f"ファイル: {f['path']}\n内容: {f['content']}\n"
                                  for f in file_contents])
            })
            
            llm_response_text = result.content
            task.llm_response_cache = llm_response_text
            self.db.commit()
            self.db.refresh(task)
            logger.info(f"タスクID {task_id} のLLM応答をDBにキャッシュしました。")

            # 7. 応答を返す (この部分は変更なし)
            return {
                "file_found": bool(file_contents), # file_contentsが空でないかを判定
                "llm_response": result.content,
                "raw_files": file_contents
            }

        except Exception as e:
            logger.error(f"関連ファイル検索中にエラー発生: {e}")
            return {
                "file_found": False,
                "error": f"検索処理中にエラーが発生しました: {str(e)}"
            }
            
            
            
            
            
            
   # def find_related_file_for_task(self, task_id: int):
    #     """指定されたタスクIDに関連するファイルを探す"""
    #     logger.info(f"タスクID {task_id} の関連ファイル検索を開始")
    
    #     # 1. タスク情報の取得
    #     task = self.db.query(TodoModel).filter(TodoModel.id == task_id).first()
    #     logger.info('タスクが見つかりました')
    #     if not task:
    #         logger.warning(f"タスクID {task_id} が見つかりません")
    #         return None

    #     # 2. 検索対象ディレクトリの確認
    #     if not search_directory or not os.path.exists(search_directory):
    #         logger.error(f"検索ディレクトリが無効です: {search_directory}")
    #         return {"error": "検索ディレクトリが設定されていないか、存在しません"}

    #     # 3. タスク情報を準備
    #     task_context = (
    #         f"タイトル: {task.title}\n"
    #         f"説明: {task.description}\n"
    #         f"期限: {task.time_limit}\n"
    #     )

    #     # 4. ファイル一覧の取得と内容の読み込み
    #     file_contents = []
        
    #     # file_contentsがそもそもDBにある可能性を考慮する。
                        
            
    #     for root, _, files in os.walk(search_directory):
    #         for file in files:
    #             if file.endswith(('.txt', '.md', '.py', '.js', '.html', '.css')):
    #                 file_path = os.path.join(root, file)
    #                 try:
    #                     with open(file_path, 'r', encoding='utf-8') as f:
    #                         content = f.read()
    #                         file_contents.append({
    #                             'path': os.path.relpath(file_path, search_directory),
    #                             'content': content[:1000]
    #                         })
    #                 except Exception as e:
    #                     logger.warning(f"ファイル {file_path} の読み込みに失敗: {e}")

    #     try:
    #         # 5. LLMで関連性を判定
    #         result = self.chain.invoke({
    #             "task_info": task_context,
    #             "files": "\n".join([f"ファイル: {f['path']}\n内容: {f['content']}\n" 
    #                               for f in file_contents])
    #         })

    #         # 6. 応答の解析（シンプルなテキスト形式）
    #         return {
    #             "file_found": True,
    #             "llm_response": result.content,
    #             "raw_files": file_contents
            # }