from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_todo import router as todo_router
from app.api.routes_schedule import router as schedule_router
from app.database import engine, Base  # ← 追加

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todo_router, prefix="/api/todo", tags=["Todo"])
app.include_router(schedule_router, prefix="/api/schedule", tags=["Schedule"])


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
