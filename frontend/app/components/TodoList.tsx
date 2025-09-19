// frontend/app/components/TodoList.tsx
"use client";
import { useState, useEffect } from "react";
import { deleteTodo, Todo, updateTodo } from "../api/todoApi";
import { optimizeSchedule } from "../api/scheduleApi";
import styles from './TodoList.module.css'; // CSSモジュールをインポート


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
const handleTaskClick = async (taskId: number) => {
  // バックエンドのAPIを呼び出す
  console.log('呼び出し開始')
  console.log(`/api/schedule/${taskId}/related_file`)
  const response = await fetch(`http://localhost:8000/api/schedule/${taskId}/related_file`); // APIのURLは適宜調整
  const data = await response.json();
  console.log('呼び出し完了', data);

  if (data.content) {
    // 取得したファイルの中身をモーダルなどで表示する
    alert(`関連ファイル: ${data.path}\n\n${data.content}`);
  } else {
    alert(data.error || "エラーが発生しました。");
  }
};
  return (
    <div>
      <ul>
        {todos.map((todo) => (
          <li key={todo.id} 
             className={`${styles.listItem} ${todo.done ? styles.completed : ''}`}
          >
            {todo.title} / {todo.time_limit ? new Date(todo.time_limit).toLocaleString() : '期限なし'} / {todo.estimated_minutes}分 {todo.done ? "(完了)" : ""}
            <button onClick={() => handleUpdate(todo.id, { done: !todo.done })} className={`${styles.button}`}>{todo.done ? "未完了" : "完了"}</button>
            <button onClick={() => handleDelete(todo.id)} className={`${styles.button}`}>削除</button>
            <button onClick={() => onEdit(todo)} className={`${styles.button}`}>編集</button>
            <button onClick={() => handleTaskClick(todo.id)}>関連ファイルを表示</button>
          </li>
        ))}
      </ul>
      <button onClick={handleClick}>スケジュール最適化</button>
    </div>
  );
}

