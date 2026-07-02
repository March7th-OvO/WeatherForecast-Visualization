interface PageStateProps {
  message: string;
}

export function LoadingState({ message }: PageStateProps) {
  return <div className="page-state">{message}</div>;
}

export function ErrorState({ message }: PageStateProps) {
  return <div className="page-state error-state">{message}</div>;
}
