import { useSyncExternalStore } from "react";

export const REFRESH_INTERVAL_MS = Number(import.meta.env.VITE_REFRESH_INTERVAL_MS ?? 10_000);

const KEY = "offtech.autoRefresh";
const listeners = new Set<() => void>();

function read(): boolean {
  try {
    return localStorage.getItem(KEY) !== "off";
  } catch {
    return true;
  }
}

let enabled = read();

export function setAutoRefresh(value: boolean): void {
  enabled = value;
  try {
    localStorage.setItem(KEY, value ? "on" : "off");
  } catch {
  }
  listeners.forEach((l) => l());
}

export function useAutoRefreshEnabled(): boolean {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => enabled,
    () => true,
  );
}
