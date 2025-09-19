from app.services.todo_service import TodoService
from app.schemas.todo import TodoCreate


def test_create_todo():
    service = TodoService()
    todo_input = TodoCreate(title="test", description="desc", done=False)
    
    # DBがない場合はモックか簡易オブジェクトで
    db = []
    result = service.create_todo(db, todo_input)
    
    assert result.title == "test"
    assert result.done is False
