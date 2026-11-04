import { Link } from "react-router-dom";

import type { Alert } from "../api";
import { formatDateTime } from "../format";
import { SeverityBadge } from "./StatusBadge";

interface Props {
  alerts: Alert[];
  names?: Map<number, string>;
}

export function AlertsTable({ alerts, names }: Props) {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Время</th>
          {names && <th>Двигатель</th>}
          <th>Цикл</th>
          <th>Уровень</th>
          <th>Сообщение</th>
        </tr>
      </thead>
      <tbody>
        {alerts.map((a) => (
          <tr key={a.id}>
            <td className="nowrap">{formatDateTime(a.triggered_at)}</td>
            {names && (
              <td>
                <Link to={`/equipment/${a.equipment_id}`}>{names.get(a.equipment_id) ?? `#${a.equipment_id}`}</Link>
              </td>
            )}
            <td>{a.cycle}</td>
            <td>
              <SeverityBadge severity={a.severity} />
            </td>
            <td>{a.message}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
