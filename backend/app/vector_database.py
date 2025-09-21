# app/vector_db.py
import chromadb

# ベクトルデータベースのクライアントを初期化
# ローカルで動かす場合
vector_client = chromadb.Client()
