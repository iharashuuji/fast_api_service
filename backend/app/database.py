# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# 1. データベースURLの設定
# SQLiteの場合、ファイルは backend/app/db.sqlite3 に作られる
SQLALCHEMY_DATABASE_URL = "sqlite:///./db.sqlite3"

# 2. エンジンの作成
# SQLiteでは check_same_thread=False が必要
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. セッションを作成するための SessionLocal
# autocommit=False, autoflush=False は一般的な設定
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. ベースクラスの作成
# モデルはこの Base を継承して定義
Base = declarative_base()

# 5. DBセッションを取得するユーティリティ関数
# FastAPI の Depends で使用する
def get_db() -> Session:
    db = SessionLocal()  # セッション作成
    try:
        yield db         # yield で generator にすることで、依存注入可能
    finally:
        db.close()       # リクエスト後に必ずクローズ
