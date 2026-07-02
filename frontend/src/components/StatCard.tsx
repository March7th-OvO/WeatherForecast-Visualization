import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  tone: "blue" | "amber" | "hot" | "cold";
  icon: LucideIcon;
}

export function StatCard({ label, value, tone, icon: Icon }: StatCardProps) {
  return (
    <div className={`stat-card ${tone}`}>
      <span className="stat-icon" aria-hidden="true">
        <Icon size={22} />
      </span>
      <div>
        <span>{value}</span>
        <p>{label}</p>
      </div>
    </div>
  );
}
