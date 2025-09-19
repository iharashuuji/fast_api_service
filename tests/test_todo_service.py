from backend.app.services.todo_service import TodoService
from backend.app.schemas.todo import TodoCreate
import sys
from pathlib import Path

# プロジェクトルートを PYTHONPATH に追加
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "backend"))


def test_create_todo():
    service = TodoService()
    todo_input = TodoCreate(title="test", description="desc", done=False)
    
    # DBがない場合はモックか簡易オブジェクトで
    db = []
    result = service.create_todo(db, todo_input)
    
    assert result.title == "test"
    assert result.done is False
