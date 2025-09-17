// frontend/app/page.tsx
"use client";

import { useEffect, useState } from "react";
import { fetchTodos, createTodo, Todo } from "./api/todoApi";
import TodoForm from "./components/TodoForm";
import TodoList from "./components/TodoList";

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);

  const loadTodos = async () => {
    const data = await fetchTodos();
    setTodos(data);
  };

  const addTodo = async (title: string, time_limit: string, estimated_minutes: number) => {
    // バックエンドAPIをたたいて新しいTodoを作成
    const newTodo = await createTodo(title, time_limit, estimated_minutes);
    // 帰ってきたNewtodoをフロントのStateに追加
    setTodos([...todos, newTodo]);
  };

  useEffect(() => {
    loadTodos();
  }, []);

  return (
    <div>
      <h1>Todo アプリ（FastAPI + Next.js）</h1>
      <TodoForm onAdd={addTodo} />
      <TodoList todos={todos} setTodos={setTodos} />
    </div>
  );
}
