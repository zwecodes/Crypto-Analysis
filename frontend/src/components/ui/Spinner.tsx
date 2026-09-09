import "./Spinner.css";

interface SpinnerProps {
  label?: string;
}

export function Spinner({ label = "Loading..." }: SpinnerProps) {
  return (
    <div className="spinner-container" role="status" aria-live="polite">
      <div className="spinner" />
      <span className="spinner-label">{label}</span>
    </div>
  );
}
