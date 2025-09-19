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
```
今後の導入予定
```markdonw
- 緊急度の高いタスクに対する通知
- ゲーム要素（進捗に応じてポイント・レベルアップ）
- カレンダー連携（Google Calendar / Outlook）
- 日次レポート: 今日の達成度や未完了タスクの整理
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
  - API_KEY
```

### ファイル構成
```python
project/
├── backend/                       # FastAPI
│   ├── app/
│   │   ├── main.py                # FastAPI エントリーポイント
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes_todo.py     # Todo CRUD
│   │   │   └── routes_schedule.py # スケジュール最適化
│   │   ├── schemas/
│   │   │   ├── todo.py
│   │   │   └── schedule.py
│   │   └── services/
│   │       ├── todo_service.py
│   │       └── schedule_service.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                       # Next.js
│   ├── app/
│   │   ├── page.tsx                # トップページ
│   │   ├── components/
│   │   │   ├── TodoList.tsx
│   │   │   └── ScheduleView.tsx
│   │   └── api/
│   │       ├── todoApi.ts          # FastAPI Todo CRUD 呼び出し
│   │       └── scheduleApi.ts      # FastAPI スケジュール最適化呼び出し
│   ├── package.json
│   └── tsconfig.json
│
└── docker-compose.yml             # FastAPI + Next.js を統合して起動
```

