### 概要
### Smart AI todo app
あなたが今やるべき事を明確に、バイアスなくAIが決定をします。

### 技術スタック
```markdown
- FastAPI / Python 3.11
- Next.js / Typescript
- PostgreSQL
- LangChain / Google Gemini API
```

### 機能一覧（拡張版）
```markdown
- TodoのCRUD処理
- GEMINI_APIによる自然言語処理での優先順位付け
- 「作業時間入力」に応じた最適タスク提案
  - 例: 2時間作業予定 → AIが最高効率でこなせる順番を提案
- GEMINI_APIによる必要なファイルの探索と提案
  - 例: 宿題をする → AIが必要なファイルを探索して、このファイルを参照するようにサジェストする。
```


### 起動方法
```python
cd fast_ai_servie
docker-compose up --build
```

###  設定・環境変数
```markdown
## Configuration
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google AI service account key
- `.env` variables:
  - GEMINI_API_KEY
  - SEARCH_DIR
  - GOOGLE_APPLICATION_CREDENTIALS
```


### ファイル構成と役割

```
.
├── backend/                     # バックエンドアプリケーション
│   ├── app/                    # メインアプリケーションコード
│   │   ├── api/               # APIエンドポイント定義
│   │   │   ├── __init__.py
│   │   │   ├── routes_schedule.py  # スケジュール最適化エンドポイント
│   │   │   └── routes_todo.py      # Todo CRUD操作エンドポイント
│   │   ├── models/            # データベースモデル
│   │   │   ├── __init__.py
│   │   │   └── todo_model.py  # Todoテーブル定義
│   │   ├── schemas/           # APIリクエスト/レスポンスの型定義
│   │   │   ├── __init__.py
│   │   │   ├── schedule.py    # スケジュール関連のスキーマ
│   │   │   └── todo.py        # TodoのCRUD操作用スキーマ
│   │   ├── services/          # ビジネスロジック
│   │   │   ├── __init__.py
│   │   │   ├── schdule_service.py  # Gemini APIを使用したスケジュール最適化
│   │   │   └── todo_service.py     # Todo操作の基本ロジック
│   │   ├── __init__.py
│   │   ├── database.py        # SQLiteデータベース設定
│   │   └── main.py           # FastAPIアプリケーション設定
│   ├── tests/                 # テストコード
│   │   ├── __init__.py
│   │   ├── conftest.py       # テスト環境設定
│   │   └── test_todo_service.py  # Todoサービスのユニットテスト
│   └── requirements.txt       # Python依存パッケージ
├── frontend/                  # フロントエンドアプリケーション
│   ├── app/                  # Next.jsアプリケーション
│   │   ├── api/             # バックエンドAPI呼び出し
│   │   │   ├── scheduleApi.ts  # スケジュール最適化API
│   │   │   └── todoApi.ts      # Todo CRUD API
│   │   ├── components/      # Reactコンポーネント
│   │   │   ├── EditTodo.tsx    # Todo編集UI
│   │   │   ├── ScheduleView.tsx # スケジュール表示
│   │   │   ├── TodoForm.tsx     # Todo作成フォーム
│   │   │   └── TodoList.tsx     # Todoリスト表示
│   │   ├── layout.tsx       # 共通レイアウト
│   │   └── page.tsx         # メインページ
│   ├── Dockerfile           # フロントエンドのコンテナ設定
│   ├── next.config.js       # Next.js設定
│   ├── package.json         # npm依存パッケージ
│   └── tsconfig.json        # TypeScript設定
└── docker-compose.yml       # アプリケーション全体のコンテナ設定
```

### 主要コンポーネントの説明

#### バックエンド

**API層 (`backend/app/api/`)**
- `routes_todo.py`: TodoのCRUD操作を提供するRESTful API
- `routes_schedule.py`: Gemini APIを活用したスケジュール最適化APIを提供

**データモデル (`backend/app/models/`)**
- `todo_model.py`: SQLAlchemyを使用したTodoテーブルの定義
  - タイトル、説明、完了状態、期限、見積時間、優先度などを管理

**スキーマ (`backend/app/schemas/`)**
- `todo.py`: APIの入出力データ型を定義
  - `TodoCreate`: 新規Todo作成用
  - `TodoUpdate`: Todo更新用
  - `TodoOut`: APIレスポンス用
- `schedule.py`: スケジュール最適化用のデータ型

**サービス層 (`backend/app/services/`)**
- `todo_service.py`: Todoの基本的なデータベース操作を実装
- `schdule_service.py`: Gemini APIを使用した高度なスケジュール最適化ロジック
  - タスクの優先順位付け
  - 作業時間に基づく最適なタスク配分
  - AIによるタスク実行順序の提案

#### フロントエンド

**APIクライアント (`frontend/app/api/`)**
- `todoApi.ts`: バックエンドのTodo APIとの通信を管理
- `scheduleApi.ts`: スケジュール最適化機能の呼び出しを担当

**UIコンポーネント (`frontend/app/components/`)**
- `TodoList.tsx`: Todoリストの表示と管理
- `TodoForm.tsx`: 新規Todo作成インターフェース
- `EditTodo.tsx`: 既存Todoの編集機能
- `ScheduleView.tsx`: AI最適化されたスケジュールの可視化

```

