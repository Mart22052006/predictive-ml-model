import { useCallback, useEffect, useRef, useState } from "react";

import { REFRESH_INTERVAL_MS, useAutoRefreshEnabled } from "./autoRefresh";
import { isSame, nextDelay } from "./liveFetchLogic";

interface LiveOptions {
  /** Интервал опроса, мс (по умолчанию VITE_REFRESH_INTERVAL_MS или 10 000). 0 — без автообновления. */
  intervalMs?: number;
}

/**
 * Замена useFetch с автообновлением: данные подтягиваются в фоне, пока открыта страница.
 * Возвращает то же, что useFetch ({ data, error, loading, reload, setData }),
 * плюс { refreshing, updatedAt, refreshError }.
 *
 * - `loading` — только первая загрузка (в фоне экран не мигает «Загрузка…»);
 * - `reload` (кнопка «Обновить») обновляет в фоне: данные остаются на экране, `refreshing = true`;
 * - если данные не изменились, объект `data` остаётся прежним — графики не перерисовываются;
 * - вкладка скрыта — опрос на паузе, при возвращении обновляем сразу;
 * - при сбое остаются последние данные (`refreshError`), опрос замедляется до 60 с;
 * - `error` — только если данных ещё нет (первая загрузка не удалась); опрос при этом продолжается
 *   и сам восстановит экран, как только сервер ответит.
 */
export function useLiveFetch<T>(fn: () => Promise<T>, deps: unknown[], options: LiveOptions = {}) {
  const intervalMs = options.intervalMs ?? REFRESH_INTERVAL_MS;
  const auto = useAutoRefreshEnabled();

  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  const run = useCallback(fn, deps);
  const runRef = useRef(run);
  runRef.current = run;
  const requestId = useRef(0); // номер последнего запроса: ответы от устаревших игнорируются
  const failures = useRef(0);
  const timer = useRef<number | undefined>(undefined);
  const hasData = useRef(false);

  const load = useCallback(async (background: boolean) => {
    const id = ++requestId.current;
    if (background) setRefreshing(true);
    else setLoading(true);
    try {
      const next = await runRef.current();
      if (id !== requestId.current) return;
      failures.current = 0;
      hasData.current = true;
      setData((prev) => (prev !== null && isSame(prev, next) ? prev : next));
      setError(null);
      setUpdatedAt(new Date());
    } catch (e) {
      if (id !== requestId.current) return;
      failures.current += 1;
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      if (id === requestId.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, []);

  // Первая загрузка и перезагрузка при смене зависимостей (например, другой двигатель)
  useEffect(() => {
    failures.current = 0;
    hasData.current = false;
    setData(null);
    setError(null);
    void load(false);
    return () => {
      requestId.current += 1;
    };
  }, [load, run]);

  // Периодический опрос
  useEffect(() => {
    if (!auto || intervalMs <= 0) return;
    let stopped = false;

    const schedule = () => {
      timer.current = window.setTimeout(async () => {
        if (stopped) return;
        if (!document.hidden) await load(true);
        if (!stopped) schedule();
      }, nextDelay(intervalMs, failures.current));
    };
    const onVisible = () => {
      if (document.hidden) return;
      window.clearTimeout(timer.current);
      void load(true).then(() => {
        if (!stopped) schedule();
      });
    };

    schedule();
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      stopped = true;
      window.clearTimeout(timer.current);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [auto, intervalMs, load]);

  const reload = useCallback(() => {
    void load(hasData.current);
  }, [load]);

  return {
    data,
    error: data === null ? error : null,
    loading,
    reload,
    setData,
    refreshing,
    updatedAt,
    refreshError: data !== null ? error : null,
  };
}
