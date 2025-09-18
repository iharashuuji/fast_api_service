from sqlalchemy.orm import Session
from typing import List
from app.models.todo_model import TodoModel
from app.schemas.todo import TodoCreate, TodoOut

class TodoService:
    def get_all_todos(self, db: Session) -> List[TodoModel]:
        return db.query(TodoModel).all()

    def create_todo(self, db: Session, todo: TodoCreate) -> TodoModel:
        db_todo = TodoModel(title=todo.title, time_limit=todo.time_limit, estimated_minutes=todo.estimated_minutes, done=False)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    def update_todo(self, db: Session, todo_id: int, todo: TodoCreate) -> TodoModel:
        db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not db_todo:
            raise ValueError("Todo not found")
        update_data = todo.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_todo, key, value)
        # Alternatively, you can update specific fields like this:
        db.commit()
        db.refresh(db_todo)
        return db_todo

    def delete_todo(self, db: Session, todo_id: int) -> bool:
        db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not db_todo:
            return False
        db.delete(db_todo)
        db.commit()
        return True
