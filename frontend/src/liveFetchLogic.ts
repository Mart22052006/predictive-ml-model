export function nextDelay(baseMs: number, failures: number, maxMs = 60_000): number {
  return Math.min(baseMs * 2 ** failures, Math.max(maxMs, baseMs));
}

export function isSame(a: unknown, b: unknown): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

export const formatTime = (d: Date): string => d.toLocaleTimeString("ru-RU");
