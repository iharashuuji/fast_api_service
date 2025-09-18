// frontend/app/api/scheduleApi.ts
import { Todo } from './todoApi';

const BASE_URL = "http://localhost:8000/api/schedule";

export const fetchSchedule = async (): Promise<Todo[]> => {
  const res = await fetch(BASE_URL);
  return res.json();
};

export const optimizeSchedule = async (date: string): Promise<Todo[]> => {
  const res = await fetch(`${BASE_URL}/optimize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ date }),
  });
  
  if (!res.ok) {
    throw new Error(`スケジュール最適化に失敗しました: ${res.statusText}`);
  }
  
  return res.json();
};
