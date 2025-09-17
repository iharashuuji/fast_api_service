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
