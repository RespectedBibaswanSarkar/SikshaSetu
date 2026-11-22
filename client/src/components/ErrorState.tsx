interface ErrorStateProps {
  message?: string;
  onRetry: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="error-state" data-testid="error-state" role="alert">
      <div className="error-state-icon" aria-hidden="true">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h2 className="error-state-title">Hub Unreachable</h2>
      <p className="error-state-msg">
        {message ?? "Cannot connect to SikshaSetu backend. Make sure the hub is running."}
      </p>
      <button className="btn-primary" data-testid="retry" onClick={onRetry}>
        Retry Connection
      </button>
    </div>
  );
}
