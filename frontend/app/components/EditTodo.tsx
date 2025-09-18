// app/EditTodo.tsx
"use client";
import { useState } from "react";
import { updateTodo, Todo } from "../api/todoApi";
export default function EditTodo({ todo, onUpdate, onClose }) {
  const [title, setTitle] = useState(todo.title);

  // タイトル以外のInputを追加する
  const [timeLimit, setTimeLimit] = useState(
    todo.time_limit ? todo.time_limit.slice(0, 16) : ""
  );
  const [estimatedMinutes, setEstimatedMinutes] = useState(
    todo.estimated_minutes || 0
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const updated = await updateTodo(todo.id, {
        title, time_limit: timeLimit ? new Date(timeLimit).toISOString() : null, estimated_minutes: estimatedMinutes
    })
    onUpdate(todo.id, { title, time_limit: timeLimit, estimated_minutes: estimatedMinutes });
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <form onSubmit={handleSubmit}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
            <input type="datetime-local"
              value={timeLimit}
              onChange={(e) => setTimeLimit(e.target.value)}
            />
            <input type="number"
              value={estimatedMinutes}
              onChange={(e) => setEstimatedMinutes(Number(e.target.value))}
            />
          <button type="submit">更新</button>
          <button type="button" onClick={onClose}>閉じる</button>
        </form>
      </div>
    </div>
  );
}
type Props = {
  todo: Todo;
  onUpdate: (id: number, updates: Partial<Todo>) => void;
  onClose: () => void;
};

