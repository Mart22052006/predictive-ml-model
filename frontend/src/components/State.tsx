export function Loading() {
  return <p className="muted">Загрузка…</p>;
}

export function ErrorMessage({ message }: { message: string }) {
  return <p className="error">Ошибка: {message}</p>;
}

export function Empty({ text }: { text: string }) {
  return <p className="muted">{text}</p>;
}
