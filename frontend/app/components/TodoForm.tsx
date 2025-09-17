// frontend/app/components/TodoForm.tsx
"use client";

import { useState } from "react";

type Props = {
  onAdd: (title: string, time_limit: string, estimated_minutes: number) => void;
};

export default function TodoForm({ onAdd }: Props) {
  const [title, setTitle] = useState("");
  const [timeLimit, setTimeLimit] = useState("");
  const [estimatedMinutes, setEstimatedMinutes] = useState(0);


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onAdd(title, timeLimit, estimatedMinutes);
      setTitle("");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="新しい Todo"
      />
      <input
        type="datetime-local"
        value={timeLimit}
        onChange={(e) => setTimeLimit(e.target.value)}
        placeholder="期限"
      />
      <input
        type="number"
        value={estimatedMinutes}
        onChange={(e) => setEstimatedMinutes(Number(e.target.value))}
        placeholder="所要時間 (分)"
      />
      <button type="submit">追加</button>
    </form>
  );
}

