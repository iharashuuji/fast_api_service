// frontend/app/page.tsx
"use client";

import { useEffect, useState } from "react";
import { fetchTodos, createTodo, updateTodo, Todo } from "./api/todoApi";
import TodoForm from "./components/TodoForm";
import TodoList from "./components/TodoList";
import EditTodo from "./components/EditTodo";


export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null); // モーダルの表示/非表示を管理

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
  const handleUpdate = async (id: number, updates: Partial<Todo>) => {
    const updated = await updateTodo(id, updates);
    setTodos(todos.map((t) => (t.id === id ? updated : t)));
    setEditingTodo(null);
  };

  useEffect(() => {
    loadTodos();
  }, []);

  return (
    <div>
      <h1>Todo アプリ（FastAPI + Next.js）</h1>
      <TodoForm onAdd={addTodo} />
      <TodoList todos={todos} setTodos={setTodos} onEdit={setEditingTodo} />
    {/* ここに条件付きでモーダル表示 */}
    {editingTodo && (
      <EditTodo
        todo={editingTodo}
        onUpdate={handleUpdate}
        onClose={() => setEditingTodo(null)}
      />
    )}
    </div>
  );
}
