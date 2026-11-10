import { setAutoRefresh, useAutoRefreshEnabled } from "../autoRefresh";
import { formatTime } from "../liveFetchLogic";
import "./LiveIndicator.css";

interface Props {
  updatedAt: Date | null;
  refreshing: boolean;
  refreshError: string | null;
}

/** «Обновлено 12:03:05» + переключатель автообновления. Ставится рядом с кнопкой «Обновить». */
export function LiveIndicator({ updatedAt, refreshing, refreshError }: Props) {
  const auto = useAutoRefreshEnabled();
  const time = updatedAt ? formatTime(updatedAt) : "—";

  let text = `Обновлено ${time}`;
  let dot = "on";
  if (refreshError) {
    text = `Нет связи с сервером, показаны данные от ${time}`;
    dot = "stale";
  } else if (!auto) {
    text = `Автообновление выключено, данные от ${time}`;
    dot = "off";
  }

  return (
    <div className="live" role="status" aria-live="polite">
      <span className={`live-dot ${dot}${refreshing ? " busy" : ""}`} aria-hidden="true" />
      <span>{text}</span>
      <label className="live-toggle">
        <input type="checkbox" checked={auto} onChange={(e) => setAutoRefresh(e.target.checked)} />
        Автообновление
      </label>
    </div>
  );
}
