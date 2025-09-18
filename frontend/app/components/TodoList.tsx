// frontend/app/components/TodoList.tsx
"use client";
import { useState, useEffect } from "react";
import { deleteTodo, Todo, updateTodo } from "../api/todoApi";
import { optimizeSchedule } from "../api/scheduleApi";

type Props = {
  todos: Todo[];
  setTodos: React.Dispatch<React.SetStateAction<Todo[]>>;
  onEdit: (todo: Todo) => void; //何も返さない関数である事を明記をする。voidの役割である。
};


export default function TodoList({ todos, setTodos, onEdit }: Props) {
  const handleDelete = async (id: number) => {
  await deleteTodo(id);
  setTodos((prev) => prev.filter((todo) => todo.id !== id));
  };

  const handleUpdate = async (id: number, updates: Partial<Todo>) => {
    const updatedTodo = await updateTodo(id, updates);
    setTodos((prev) =>
      prev.map((todo) => (todo.id === id ? updatedTodo : todo))
    );
  };

  const [result, setResult] = useState(null);

  useEffect(() => {
    if (result) {
      alert(`最適化結果: ${JSON.stringify(result)}`);
    }
  }, [result]);

const handleClick = async () => {
  try {
    const today = new Date().toISOString().split("T")[0];
    const optimizedSchedule = await optimizeSchedule(today);
    console.log("最適化されたスケジュール:", optimizedSchedule);
    setTodos(optimizedSchedule);
  } catch (error) {
    console.error("スケジュール最適化中にエラーが発生しました:", error);
  }
};
  return (
    <div>
      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            {todo.title} / {todo.time_limit ? new Date(todo.time_limit).toLocaleString() : '期限なし'} / {todo.estimated_minutes}分 {todo.done ? "(完了)" : ""}
            <button onClick={() => handleUpdate(todo.id, { done: !todo.done })}>{todo.done ? "未完了" : "完了"}</button>
            <button onClick={() => handleDelete(todo.id)}>削除</button>
            <button onClick={() => onEdit(todo)}>編集</button>
          </li>
        ))}
      </ul>
      <button onClick={handleClick}>スケジュール最適化</button>
    </div>
  );
}

