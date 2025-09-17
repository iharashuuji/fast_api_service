# """
#     作成機能
#     title: str
#     description: Optional[str] = None
#     done: bool = False
#     削除機能
#     id: int  # DB に保存された ID を含める
# """


# # app/services/todo_service.py
# from typing import List
# from app.schemas.todo import TodoCreate, TodoOut

# from app.models.todo_model import TodoModel
# # 仮のデータストア（SQLiteやDBでもOK）
# db = []
# id_counter = 1

# class TodoService:
#     def get_all_todos(self) -> List[TodoOut]:
#         return db

#     def create_todo(self, todo: TodoCreate) -> TodoOut:
#         global id_counter
#         # new_todo = TodoOut(id=id_counter, **todo.dict())
#         # id_counter += 1
#         # fake_db.append(new_todo)
#         db_todo = TodoModel(title=todo.title, done=False)
#         db.add(db_todo)
#         db.commit()
#         db.refresh(db_todo)
#         return db_todo

#     def update_todo(self, todo_id: int, todo: TodoCreate) -> TodoOut:
#         for idx, t in enumerate(fake_db):
#             if t.id == todo_id:
#                 updated = TodoOut(id=todo_id, **todo.dict())
#                 fake_db[idx] = updated
#                 return updated
#         raise ValueError("Todo not found")

#     def delete_todo(self, todo_id: int) -> bool:
#         for idx, t in enumerate(fake_db):
#             if t.id == todo_id:
#                 del fake_db[idx]
#                 return True
#         return False


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

        db_todo.title = todo.title
        db_todo.done = todo.done
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
