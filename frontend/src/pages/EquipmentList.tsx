import { Link } from "react-router-dom";

import { api } from "../api";
import { Empty, ErrorMessage, Loading } from "../components/State";
import { StatusBadge } from "../components/StatusBadge";
import { formatDate, formatRul } from "../format";
import { useFetch } from "../useFetch";

export function EquipmentList() {
  const { data, error, loading, reload } = useFetch(api.listEquipment, []);

  return (
    <section>
      <div className="page-head">
        <h1>Оборудование</h1>
        <button className="btn btn-secondary" onClick={reload} disabled={loading}>
          Обновить
        </button>
      </div>

      {error && <ErrorMessage message={error} />}
      {loading && !data && <Loading />}
      {data && data.length === 0 && <Empty text="Оборудования пока нет — запустите симулятор." />}

      {data && data.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Статус</th>
              <th className="num">Прогноз RUL, циклов</th>
              <th>Последнее обслуживание</th>
            </tr>
          </thead>
          <tbody>
            {data.map((e) => (
              <tr key={e.id}>
                <td>
                  <Link to={`/equipment/${e.id}`}>{e.name}</Link>
                </td>
                <td>
                  <StatusBadge status={e.status} />
                </td>
                <td className="num">{formatRul(e.predicted_rul)}</td>
                <td>{formatDate(e.last_maintenance_date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
