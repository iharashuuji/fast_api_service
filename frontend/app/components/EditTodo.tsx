// app/EditTodo.tsx
"use client";
import { useState } from "react";
import { updateTodo, Todo } from "../api/todoApi";
import styles from './EditTodo.module.css'; // CSSモジュールをインポート

export default function EditTodo({ todo, onUpdate, onClose }: Props) { // Propsの型注釈を追加
  const [title, setTitle] = useState(todo.title);

  // タイトル以外のInputを追加する
  const [timeLimit, setTimeLimit] = useState(
    todo.time_limit ? todo.time_limit.slice(0, 16) : ""
  );
  const [estimatedMinutes, setEstimatedMinutes] = useState(
    todo.estimated_minutes || 0
  );
  const [description, setDescription] = useState(
    todo.description || ""
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const updated = await updateTodo(todo.id, {
        title, time_limit: timeLimit ? new Date(timeLimit).toISOString() : null, estimated_minutes: estimatedMinutes
    })
    onUpdate(todo.id, { title, time_limit: timeLimit, estimated_minutes: estimatedMinutes });
    onClose(); // 更新後に閉じる
  };

  return (
    <div className={styles.modalBackdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}> {/* 背景クリックで閉じないようにする */}
        <h3>タスクを編集</h3>
        <form onSubmit={handleSubmit} className={styles.form}>
            <input 
              value={title} 
              onChange={(e) => setTitle(e.target.value)}
              className={styles.input}
            />
            <input 
              type="datetime-local"
              value={timeLimit}
              onChange={(e) => setTimeLimit(e.target.value)}
              className={styles.input}
            />
            <input 
              type="number"
              value={estimatedMinutes}
              onChange={(e) => setEstimatedMinutes(Number(e.target.value))}
              className={styles.input}
            />
            <input 
              type="text"
              value={todo.description}
              onChange={(e) => setDescription(e.target.value)}
              className={styles.input}
              placeholder="タスクの詳細"
            />
            <div className={styles.buttonContainer}>
              <button type="button" onClick={onClose} className={`${styles.button} ${styles.buttonSecondary}`}>
                閉じる
              </button>
              <button type="submit" className={`${styles.button} ${styles.buttonPrimary}`}>
                更新
              </button>
            </div>
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