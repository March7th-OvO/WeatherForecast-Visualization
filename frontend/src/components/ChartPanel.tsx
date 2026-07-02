import type { ReactNode } from "react";

interface ChartPanelProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export function ChartPanel({ title, children, className = "" }: ChartPanelProps) {
  return (
    <section className={`chart-panel ${className}`} aria-label={title}>
      <div className="panel-heading">
        <h3>{title}</h3>
      </div>
      {children}
    </section>
  );
}
