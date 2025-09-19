from unittest.mock import MagicMock
from app.services.todo_service import TodoService
from app.schemas.todo import TodoCreate
from app.models.todo_model import TodoModel


def test_create_todo():
    # Mockの作成
    db = MagicMock()
    db_todo = None
    
    def mock_add(todo):
        nonlocal db_todo
        db_todo = todo
    
    db.add.side_effect = mock_add
    db.commit = MagicMock()
    db.refresh = MagicMock()
    
    # テストの実行
    service = TodoService()
    todo_input = TodoCreate(title="test", description="desc", done=False)
    result = service.create_todo(db, todo_input)
    
    # 検証
    assert isinstance(result, TodoModel)
    assert result.title == "test"
    assert result.done is False
    assert db.add.called
    assert db.commit.called
    assert db.refresh.called
