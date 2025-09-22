// // frontend/app/components/TodoList.tsx
// "use client";
// import { useState, useEffect } from "react";
// import { deleteTodo, Todo, updateTodo, OptimizationResult } from "../api/todoApi";
// import { optimizeSchedule } from "../api/scheduleApi";
// import styles from './TodoList.module.css'; // CSSモジュールをインポート


// type Props = {
//   todos: Todo[];
//   setTodos: React.Dispatch<React.SetStateAction<Todo[]>>;
//   onEdit: (todo: Todo) => void; //何も返さない関数である事を明記をする。voidの役割である。
// };

// // 取得したファイル情報を格納するための型定義
// type FileInfo = {
//   llm_response: string;
//   raw_content: string;
// };


// export default function TodoList({ todos, setTodos, onEdit }: Props) {
//   const [expandedTodoId, setExpandedTodoId] = useState<number | null>(null);
//   // 最適化関連のstate追加
//   const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
//   const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);

//   // ★ 変更点 2: 取得したファイル情報を保持するStateを追加
//   // { todoId: { llm_response: "...", raw_content: "..." } } という形式でデータを格納
//   const [fileContents, setFileContents] = useState<{ [key: number]: FileInfo | null }>({});
//   const handleDelete = async (id: number) => {
//   await deleteTodo(id);
//   setTodos((prev) => prev.filter((todo) => todo.id !== id));
//   };

//   const handleUpdate = async (id: number, updates: Partial<Todo>) => {
//     const updatedTodo = await updateTodo(id, updates);
//     setTodos((prev) =>
//       prev.map((todo) => (todo.id === id ? updatedTodo : todo))
//     );
//   };

//   const [result, setResult] = useState(null);

//   useEffect(() => {
//     if (result) {
//       alert(`最適化結果: ${JSON.stringify(result)}`);
//     }
//   }, [result]);

// // const handleClick = async () => {
// //   try {
// //     const today = new Date().toISOString().split("T")[0];
// //     const optimizedSchedule = await optimizeSchedule(today);
// //     console.log("最適化されたスケジュール:", optimizedSchedule);
// //     setTodos(optimizedSchedule);
// //   } catch (error) {
// //     console.error("スケジュール最適化中にエラーが発生しました:", error);
// //   }
// // };
//   const handleClick = async () => {
//     // ローディング開始
//     setIsOptimizing(true);
//     setOptimizationResult(null);

//     // 



// // 提案を保存するState
// const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
// // タスクリストを保存するState
// const [todos, setTodos] = useState<Todo[]>([]);

// const handleOptimizeSchedule = async () => {
//   try {
//     // このAPIは「提案オブジェクト」を返すはず
//     const result: OptimizationResult = await optimizeSchedule();

//     if (result && result.suggestion_text) {
//       // 提案オブジェクトは、提案専用のsetOptimizationResultに入れる
//       setOptimizationResult(result);
//     } else {
//       // エラー処理
//     }


//     // 

//     try {
//         // APIを呼び出し、提案オブジェクトを受け取る
//         const today = new Date().toISOString().split("T")[0];
//         const result = await optimizeSchedule(today);

//         // ★★★ 正しい処理 ★★★
//         // 提案オブジェクトを、提案表示専用のStateに保存する
//         setOptimizationResult(result);
        
//         // ★ ここでは setTodos() は一切呼び出さない！

//     } catch (error) {
//         console.error("スケジュール最適化中にエラーが発生しました:", error);
//         setOptimizationResult({ error: "提案の取得に失敗しました。" });
//     } finally {
//         // ローディング終了
//         setIsOptimizing(false);
//     }


//   // ★ 変更点 3: handleTaskClickのロジックを大幅に変更
//   const handleTaskClick = async (taskId: number) => {
//     // すでに開いているタスクを再度クリックした場合は、閉じる
//     if (expandedTodoId === taskId) {
//       setExpandedTodoId(null);
//       return;
//     }

//     // まだファイル情報を取得していない場合のみ、APIを呼び出す
//     if (!fileContents[taskId]) {
//       try {
//         console.log('関連ファイル検索開始:', taskId);
//         const response = await fetch(`http://localhost:8000/api/schedule/${taskId}/related_file`);

//         if (!response.ok) {
//           throw new Error(`APIエラー: ${response.status}`);
//         }
//         const data = await response.json();
//         console.log('検索結果:', data);

//         if (data.file_found && data.llm_response) {
//           // 取得したデータをStateに保存
//           setFileContents(prev => ({
//             ...prev,
//             [taskId]: {
//               llm_response: data.llm_response.content,
//               raw_content: data.raw_files?.[0]?.content || '内容なし'
//             }
//           }));
//         } else {
//           // エラー情報も保存しておく
//           setFileContents(prev => ({ ...prev, [taskId]: null }));
//           alert(data.error || "関連ファイルが見つかりませんでした。");
//         }
//       } catch (error) {
//         console.error('関連ファイル検索エラー:', error);
//         alert('関連ファイルの検索中にエラーが発生しました。');
//         setFileContents(prev => ({ ...prev, [taskId]: null }));
//       }
//     }
//     // クリックされたタスクのIDをStateにセットし、表示を開く
//     setExpandedTodoId(taskId);
//   };

//   return (
//     <div>
//       <ul>
//         {todos.map((todo) => (
//           // keyをliの外側のFragmentに移動し、liと詳細表示をグルーピング
//           <div key={todo.id}>
//             <li className={`${styles.listItem} ${todo.done ? styles.completed : ''}`}>
//               {/* タスクのタイトルやボタンなど */}
//               <span>
//                 {todo.title} / {todo.time_limit ? new Date(todo.time_limit).toLocaleString() : '期限なし'} / {todo.estimated_minutes}分 {todo.done ? "(完了)" : ""}
//               </span>
//               <div>
//                 <button onClick={() => handleUpdate(todo.id, { done: !todo.done })} className={`${styles.button}`}>{todo.done ? "未完了" : "完了"}</button>
//                 <button onClick={() => handleDelete(todo.id)} className={`${styles.button}`}>削除</button>
//                 <button onClick={() => onEdit(todo)} className={`${styles.button}`}>編集</button>
//                 {/* ★ 変更点 4: ボタンのテキストを動的に変更 */}
//                 <button onClick={() => handleTaskClick(todo.id)} className={`${styles.button}`}>
//                   {expandedTodoId === todo.id ? "閉じる" : "関連ファイル"}
//                 </button>
//               </div>
//             </li>
//             {/* ★ 変更点 5: expandedTodoIdが現在のIDと一致する場合にファイル内容を表示 */}
//             {expandedTodoId === todo.id && (
//               <div className={styles.fileContent}>
//                 {fileContents[todo.id] ? (
//                   <>
//                     <h4>関連ファイルの情報</h4>
//                     <p className={styles.llmResponse}>{fileContents[todo.id]?.llm_response}</p>
//                     <h4>ファイル内容</h4>
//                     <pre className={styles.rawContent}>{fileContents[todo.id]?.raw_content}</pre>
//                   </>
//                 ) : (
//                   <p>関連ファイルはありませんでした。</p>
//                 )}
//               </div>
//             )}
//           </div>
//         ))}
//       </ul>
//       <button onClick={handleClick} className={`${styles.button}`}>スケジュール最適化</button>
//     </div>
//   );

// frontend/app/components/TodoList.tsx
"use client";
import { useState, useEffect } from "react";
import { deleteTodo, Todo, updateTodo, OptimizationResult } from "../api/todoApi";
import { optimizeSchedule } from "../api/scheduleApi";
import styles from './TodoList.module.css';

type Props = {
  todos: Todo[];
  setTodos: React.Dispatch<React.SetStateAction<Todo[]>>;
  onEdit: (todo: Todo) => void;
};

// 取得したファイル情報を格納するための型定義
type FileInfo = {
  llm_response: string;
  raw_content: string;
};

export default function TodoList({ todos, setTodos, onEdit }: Props) {
  const [expandedTodoId, setExpandedTodoId] = useState<number | null>(null);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [fileContents, setFileContents] = useState<{ [key: number]: FileInfo | null }>({});
  const [result, setResult] = useState<OptimizationResult | null>(null);

  useEffect(() => {
    if (result) {
      alert(`最適化結果: ${JSON.stringify(result)}`);
    }
  }, [result]);

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

const handleClick = async () => {
  setIsOptimizing(true);
  setOptimizationResult(null);

  try {
    const today = new Date().toISOString().split("T")[0];
    console.log('結果の取得開始')
    const result = await optimizeSchedule(today);
    console.log('結果の取得完了')

    // 配列の場合は最初の要素を使用
    if (Array.isArray(result)) {
      setOptimizationResult(result[0]);  // 単一の結果として保存
    } else {
      setOptimizationResult(result);  // 単一の結果の場合はそのまま保存
    }
    console.log('resultの取得完了')

  } catch (error) {
    console.error("スケジュール最適化中にエラーが発生しました:", error);
    setOptimizationResult({
      id: 0,
      suggestion_text: "提案の取得に失敗しました。",
      created_at: new Date().toISOString()
    });
  } finally {
    setIsOptimizing(false);
  }
};


  const handleTaskClick = async (taskId: number) => {
    if (expandedTodoId === taskId) {
      setExpandedTodoId(null);
      return;
    }

    if (!fileContents[taskId]) {
      try {
        console.log('関連ファイル検索開始:', taskId);
        const response = await fetch(`http://localhost:8000/api/schedule/${taskId}/related_file`);
        if (!response.ok) throw new Error(`APIエラー: ${response.status}`);
        const data = await response.json();
        console.log('検索結果:', data);

        if (data.file_found && data.llm_response) {
          setFileContents(prev => ({
            ...prev,
            [taskId]: {
              llm_response: data.llm_response.content,
              raw_content: data.raw_files?.[0]?.content || '内容なし'
            }
          }));
        } else {
          setFileContents(prev => ({ ...prev, [taskId]: null }));
          alert(data.error || "関連ファイルが見つかりませんでした。");
        }
      } catch (error) {
        console.error('関連ファイル検索エラー:', error);
        alert('関連ファイルの検索中にエラーが発生しました。');
        setFileContents(prev => ({ ...prev, [taskId]: null }));
      }
    }

    setExpandedTodoId(taskId);
  };

  return (
    <div>
      <ul>
        {todos.map((todo) => (
          <div key={todo.id}>
            <li className={`${styles.listItem} ${todo.done ? styles.completed : ''}`}>
              <span>
                {todo.title} / {todo.time_limit ? new Date(todo.time_limit).toLocaleString() : '期限なし'} / {todo.estimated_minutes}分 {todo.done ? "(完了)" : ""}
              </span>
              <div>
                <button onClick={() => handleUpdate(todo.id, { done: !todo.done })} className={styles.button}>
                  {todo.done ? "未完了" : "完了"}
                </button>
                <button onClick={() => handleDelete(todo.id)} className={styles.button}>削除</button>
                <button onClick={() => onEdit(todo)} className={styles.button}>編集</button>
                <button onClick={() => handleTaskClick(todo.id)} className={styles.button}>
                  {expandedTodoId === todo.id ? "閉じる" : "関連ファイル"}
                </button>
              </div>
            </li>
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
      <button onClick={handleClick} className={styles.button}>スケジュール最適化</button>
    {optimizationResult && (
      <div className={styles.optimizationResult}>
        <h3>最適化結果</h3>
        {"error" in optimizationResult ? (
          <p>{optimizationResult.error}</p>
        ) : (
          <>
            <p>{optimizationResult.suggestion_text}</p>
            <p>
              <small>
                生成日時:{" "}
                {new Date(optimizationResult.created_at).toLocaleString()}
              </small>
            </p>
          </>
        )}
      </div>
    )}
  </div>
  );
}