// frontend/app/components/TodoList.tsx
"use client";
import { useState, useEffect } from "react";
import { deleteTodo, Todo } from "../api/todoApi";

type Props = {
  todos: Todo[];
  setTodos: React.Dispatch<React.SetStateAction<Todo[]>>;
};


export default function TodoList({ todos, setTodos }: Props) {
  const handleDelete = async (id: number) => {
  await deleteTodo(id);
  setTodos((prev) => prev.filter((todo) => todo.id !== id));
  };
  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          {todo.title} / {todo.time_limit} / {todo.estimated_minutes}分 {todo.done ? "(完了)" : ""}
          <button onClick={() => handleDelete(todo.id)}>削除</button>
        </li>
      ))}
    </ul>
  );
}


