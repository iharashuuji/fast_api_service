// frontend/app/components/TodoList.tsx
"use client";
import { useState, useEffect } from "react";
import { deleteTodo, Todo, updateTodo } from "../api/todoApi";

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
  const today = new Date().toISOString().split("T")[0];
  const res = await fetch("http://localhost:8000/optimize_schedule", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date: today }),
  });
  const optimizedTodos = await res.json();
  console.log("APIから返ってきた値:", optimizedTodos); // 👈 ここで確認
  setTodos(optimizedTodos);
};
  return (
    <div>
    <ul>
      {todos.map((todo) => (
        <div key={todo.id}>
          <li key={todo.id}>
            {todo.title} / {todo.time_limit} / {todo.estimated_minutes}分 {todo.done ? "(完了)" : ""}
            <button onClick={() => handleUpdate(todo.id, { done: !todo.done })}>{todo.done ? "未完了" : "完了"}</button>
            <button onClick={() => handleDelete(todo.id)}>削除</button>
            <button onClick={() => onEdit(todo)}>編集</button>
          </li>
        </div>
      ))}
    </ul>
    <button onClick={handleClick}>スケジュール最適化</button>
    </div>
  );
}



