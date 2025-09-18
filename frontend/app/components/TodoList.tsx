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
  try {
    const today = new Date().toISOString().split("T")[0];
    const res = await fetch("http://localhost:8000/api/schedule/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date: today }),
    });
    const data = await res.json();
    console.log("APIから返ってきた値:", data); // デバッグ用

    // データが配列でない場合の処理
    if (!Array.isArray(data)) {
      console.error("APIレスポンスが配列ではありません:", data);
      return;
    }

    // 各要素がTodo型を満たしているか確認
    const validTodos = data.filter(item => 
      typeof item === 'object' && 
      item !== null &&
      'id' in item &&
      'title' in item
    );

    if (validTodos.length === 0) {
      console.error("有効なTodoデータがありません");
      return;
    }

    setTodos(validTodos);
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

