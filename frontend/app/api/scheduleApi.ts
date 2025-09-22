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

const getRelatedFile = async (taskId: number) => {
  try {
    console.log('呼び出し開始');
    console.log(`/api/schedule/${taskId}/related_file`);
    
    const response = await fetch(
      `http://localhost:8000/api/schedule/${taskId}/related_file`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`APIエラー: ${response.status}`);
    }

    const data = await response.json();
    console.log('呼び出し完了', data);
    return data;
  } catch (error) {
    console.error('関連ファイル取得エラー:', error);
    throw error;
  }
};