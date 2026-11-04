import type { Status } from "../api";
import { SEVERITY_LABEL, STATUS_LABEL } from "../format";

export function StatusBadge({ status, large = false }: { status: Status; large?: boolean }) {
  return <span className={`badge badge-${status}${large ? " badge-large" : ""}`}>{STATUS_LABEL[status]}</span>;
}

export function SeverityBadge({ severity }: { severity: string }) {
  const cls = severity === "critical" ? "critical" : severity === "warning" ? "warning" : "info";
  return <span className={`badge badge-${cls}`}>{SEVERITY_LABEL[severity] ?? severity}</span>;
}
