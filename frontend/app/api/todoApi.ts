
// frontend/app/api/todoApi.ts
"use client";

export type Todo = {
  id: number;
  title: string;
  done: boolean;
  time_limit: string | null;
  estimated_minutes: number | null;
  description: string | null;
};

// 1. スケジュール最適化の成功結果の型
type SuccessResult = {
  id: number;
  suggestion_text: string;
  created_at: string;
  confidence_score?: number;  // 信頼度スコア（オプショナル）
  task_ids?: number[];       // 関連するタスクのID配列
};

// 2. エラー結果の型
type ErrorResult = {
  error: string;
};

// 3. 最適化結果の共用型
export type OptimizationResult = SuccessResult | ErrorResult;


const BASE_URL = "http://localhost:8000/api/todo";

export const fetchTodos = async (): Promise<Todo[]> => {
  const res = await fetch(BASE_URL);
  return res.json();
};


export const createTodo = async (
  title: string,
  time_limit: string,
  estimated_minutes: number
): Promise<Todo> => {
  const body = { title, time_limit, estimated_minutes };

  // 👇 関数の中に置く！
  console.log("📤 Sending body:", body); // デバッグ用ログ

  const res = await fetch(BASE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  console.log("📥 Response:", data); // デバッグ用ログ

  return data;
};



export const deleteTodo = async (id: number) => {
  await fetch(`${BASE_URL}/${id}`, {
    method: "DELETE",
  });
}

export const updateTodo = async (
  id: number, 
  updates: Partial<Todo>
) => {
  const res = await fetch(`${BASE_URL}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  return res.json();
}
