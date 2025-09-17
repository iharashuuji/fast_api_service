// frontend/app/api/scheduleApi.ts
export type Schedule = {
  id: number;
  task: string;
  start_time: string;
  end_time: string;
};

const BASE_URL = "http://localhost:8000/api/schedule";

export const fetchSchedule = async (): Promise<Schedule[]> => {
  const res = await fetch(BASE_URL);
  return res.json();
};

export const optimizeSchedule = async (): Promise<Schedule[]> => {
  const res = await fetch(`${BASE_URL}/optimize`, {
    method: "POST",
  });
  return res.json();
};

const handleDelete = async (id: number) => {
  await fetch(`http://localhost:8000/api/todo/${id}`, {
    method: "DELETE",
  });
  // stateからも削除して UI 更新
  setTodos((prev) => prev.filter((todo) => todo.id !== id));
};
