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

// 取得したファイル情報を格納するための型定義
type FileInfo = {
  llm_response: string;
  raw_content: string;
};


export default function TodoList({ todos, setTodos, onEdit }: Props) {
  const [expandedTodoId, setExpandedTodoId] = useState<number | null>(null);

  // ★ 変更点 2: 取得したファイル情報を保持するStateを追加
  // { todoId: { llm_response: "...", raw_content: "..." } } という形式でデータを格納
  const [fileContents, setFileContents] = useState<{ [key: number]: FileInfo | null }>({});
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
// const handleTaskClick = async (taskId: number) => {
//   // バックエンドのAPIを呼び出す
//   console.log('呼び出し開始')
//   console.log(`/api/schedule/${taskId}/related_file`)
//   const response = await fetch(`http://localhost:8000/api/schedule/${taskId}/related_file`); // APIのURLは適宜調整
//   const data = await response.json();
//   console.log('呼び出し完了', data);

//   if (data.content) {
//     // 取得したファイルの中身をモーダルなどで表示する
//     alert(`関連ファイル: ${data.path}\n\n${data.content}`);
//   } else {
//     alert(data.error || "エラーが発生しました。");
//   }
// };
// const handleTaskClick = async (taskId: number) => {
//   try {
//     console.log('関連ファイル検索開始:', taskId);
    
//     const response = await fetch(
//       `http://localhost:8000/api/schedule/${taskId}/related_file`,
//       {
//         method: 'GET',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         credentials: 'include'  // 必要に応じて
//       }
//     );

//     if (!response.ok) {
//       throw new Error(`APIエラー: ${response.status}`);
//     }

//     const data = await response.json();
//     console.log('検索結果:', data);

//     if (data.file_found && data.llm_response) {
//       // モーダル表示の改善（alertの代わりに）
//       const message = `
// 関連ファイルが見つかりました

// ${data.llm_response}

// ファイル内容:
// ${data.raw_files?.[0]?.content || '内容なし'}
//       `;
      
//       // TODO: ここでモーダルコンポーネントを使用
//       alert(message);  // 一時的にalertを使用
//     } else {
//       alert(data.error || "関連ファイルが見つかりませんでした。");
//     }
//   } catch (error) {
//     console.error('関連ファイル検索エラー:', error);
//     alert('関連ファイルの検索中にエラーが発生しました。');
//   }
// };
//   return (
//     <div>
//       <ul>
//         {todos.map((todo) => (
//           <li key={todo.id} 
//              className={`${styles.listItem} ${todo.done ? styles.completed : ''}`}
//           >
//             {todo.title} / {todo.time_limit ? new Date(todo.time_limit).toLocaleString() : '期限なし'} / {todo.estimated_minutes}分 {todo.done ? "(完了)" : ""}
//             <button onClick={() => handleUpdate(todo.id, { done: !todo.done })} className={`${styles.button}`}>{todo.done ? "未完了" : "完了"}</button>
//             <button onClick={() => handleDelete(todo.id)} className={`${styles.button}`}>削除</button>
//             <button onClick={() => onEdit(todo)} className={`${styles.button}`}>編集</button>
//             <button onClick={() => handleTaskClick(todo.id)} className={`${styles.button}`}>関連ファイルを表示</button>
//           </li>
//         ))}
//       </ul>
//       <button onClick={handleClick} className={`${styles.button}`}>スケジュール最適化</button>
//     </div>
//   );
// }


  // ★ 変更点 3: handleTaskClickのロジックを大幅に変更
  const handleTaskClick = async (taskId: number) => {
    // すでに開いているタスクを再度クリックした場合は、閉じる
    if (expandedTodoId === taskId) {
      setExpandedTodoId(null);
      return;
    }

    // まだファイル情報を取得していない場合のみ、APIを呼び出す
    if (!fileContents[taskId]) {
      try {
        console.log('関連ファイル検索開始:', taskId);
        const response = await fetch(`http://localhost:8000/api/schedule/${taskId}/related_file`);

        if (!response.ok) {
          throw new Error(`APIエラー: ${response.status}`);
        }
        const data = await response.json();
        console.log('検索結果:', data);

        if (data.file_found && data.llm_response) {
          // 取得したデータをStateに保存
          setFileContents(prev => ({
            ...prev,
            [taskId]: {
              llm_response: data.llm_response.content,
              raw_content: data.raw_files?.[0]?.content || '内容なし'
            }
          }));
        } else {
          // エラー情報も保存しておく
          setFileContents(prev => ({ ...prev, [taskId]: null }));
          alert(data.error || "関連ファイルが見つかりませんでした。");
        }
      } catch (error) {
        console.error('関連ファイル検索エラー:', error);
        alert('関連ファイルの検索中にエラーが発生しました。');
        setFileContents(prev => ({ ...prev, [taskId]: null }));
      }
    }
    // クリックされたタスクのIDをStateにセットし、表示を開く
    setExpandedTodoId(taskId);
  };

  return (
    <div>
      <ul>
        {todos.map((todo) => (
          // keyをliの外側のFragmentに移動し、liと詳細表示をグルーピング
          <div key={todo.id}>
            <li className={`${styles.listItem} ${todo.done ? styles.completed : ''}`}>
              {/* タスクのタイトルやボタンなど */}
              <span>
                {todo.title} / {todo.time_limit ? new Date(todo.time_limit).toLocaleString() : '期限なし'} / {todo.estimated_minutes}分 {todo.done ? "(完了)" : ""}
              </span>
              <div>
                <button onClick={() => handleUpdate(todo.id, { done: !todo.done })} className={`${styles.button}`}>{todo.done ? "未完了" : "完了"}</button>
                <button onClick={() => handleDelete(todo.id)} className={`${styles.button}`}>削除</button>
                <button onClick={() => onEdit(todo)} className={`${styles.button}`}>編集</button>
                {/* ★ 変更点 4: ボタンのテキストを動的に変更 */}
                <button onClick={() => handleTaskClick(todo.id)} className={`${styles.button}`}>
                  {expandedTodoId === todo.id ? "閉じる" : "関連ファイル"}
                </button>
              </div>
            </li>
            {/* ★ 変更点 5: expandedTodoIdが現在のIDと一致する場合にファイル内容を表示 */}
            {expandedTodoId === todo.id && (
              <div className={styles.fileContent}>
                {fileContents[todo.id] ? (
                  <>
                    <h4>関連ファイルの情報</h4>
                    <p className={styles.llmResponse}>{fileContents[todo.id]?.llm_response}</p>
                    <h4>ファイル内容</h4>
                    <pre className={styles.rawContent}>{fileContents[todo.id]?.raw_content}</pre>
                  </>
                ) : (
                  <p>関連ファイルはありませんでした。</p>
                )}
              </div>
            )}
          </div>
        ))}
      </ul>
      <button onClick={handleClick} className={`${styles.button}`}>スケジュール最適化</button>
    </div>
  );
}