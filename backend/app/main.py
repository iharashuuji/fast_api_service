from fastapi import FastAPI
# CORS設定　Next.jsと通信をする為のもの
from fastapi.middleware.cors import CORSMiddleware
from app.models import todo_model  # ← モデルを import して登録
app = FastAPI()
from app.api.routes_todo import router as todo_router
from app.api.routes_schedule import router as schedule_router

app.include_router(todo_router, prefix="/api/todo", tags=["Todo"])
app.include_router(schedule_router, prefix="/api/schedule", tags=["Schedule"])

from app.database import engine, Base  # ← 追加

Base.metadata.create_all(bind=engine)
# CORS設定　Next.jsと通信をする為のもの
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# main.py 内で直接実行する場合
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
