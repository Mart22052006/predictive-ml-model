import { useMemo } from "react";

import { api } from "../api";
import { AlertsTable } from "../components/AlertsTable";
import { Empty, ErrorMessage, Loading } from "../components/State";
import { useFetch } from "../useFetch";

export function Alerts() {
  const alerts = useFetch(() => api.listAlerts(200), []);
  const equipment = useFetch(api.listEquipment, []);

  const names = useMemo(
    () => new Map((equipment.data ?? []).map((e) => [e.id, e.name])),
    [equipment.data],
  );

  return (
    <section>
      <div className="page-head">
        <h1>Алерты</h1>
        <button className="btn btn-secondary" onClick={alerts.reload} disabled={alerts.loading}>
          Обновить
        </button>
      </div>

      {alerts.error && <ErrorMessage message={alerts.error} />}
      {alerts.loading && !alerts.data && <Loading />}
      {alerts.data && alerts.data.length === 0 && <Empty text="Алертов нет." />}
      {alerts.data && alerts.data.length > 0 && <AlertsTable alerts={alerts.data} names={names} />}
    </section>
  );
}
