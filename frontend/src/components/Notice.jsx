export default function Notice({ message, type = "info", onClose }) {
  if (!message) return null;
  return <div className={`notice notice-${type}`} role="status"><span>{message}</span>{onClose && <button onClick={onClose} aria-label="Dismiss">×</button>}</div>;
}