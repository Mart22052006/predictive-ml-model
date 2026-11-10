export type Status = "normal" | "warning" | "critical";

export interface Equipment {
  id: number;
  name: string;
  type: string;
  unit_number: number;
  last_maintenance_date: string | null;
  current_cycle: number;
  status: Status;
  predicted_rul: number;
}

export interface EquipmentStatus {
  equipment_id: number;
  status: Status;
  current_cycle: number;
  predicted_rul: number;
  defect_probability: number;
  residual: number;
}

export interface Reading {
  cycle: number;
  sensors: Record<string, number>;
}

export interface PhysicsPoint {
  cycle: number;
  expected: number;
  actual: number;
  residual: number;
}

export interface ForecastPoint {
  cycle: number;
  rul: number;
  rul_low: number;
  rul_high: number;
}

export interface Forecast {
  equipment_id: number;
  current_cycle: number;
  predicted_rul: number;
  predicted_failure_cycle: number;
  points: ForecastPoint[];
}

export interface Alert {
  id: number;
  equipment_id: number;
  cycle: number;
  triggered_at: string;
  severity: "info" | "warning" | "critical";
  message: string;
}

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, init);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {}
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listEquipment: () => request<Equipment[]>("/equipment"),
  getEquipment: (id: number) => request<Equipment>(`/equipment/${id}`),
  getHistory: (id: number, limit = 500) => request<Reading[]>(`/equipment/${id}/history?limit=${limit}`),
  getForecast: (id: number) => request<Forecast>(`/equipment/${id}/forecast`),
  getPhysics: (id: number, limit = 500) => request<PhysicsPoint[]>(`/equipment/${id}/physics?limit=${limit}`),
  listAlerts: (limit = 100) => request<Alert[]>(`/alerts?limit=${limit}`),
  alertsByEquipment: (id: number, limit = 50) => request<Alert[]>(`/alerts/${id}?limit=${limit}`),
  predict: (id: number) =>
    request<EquipmentStatus>("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ equipment_id: id }),
    }),
};
