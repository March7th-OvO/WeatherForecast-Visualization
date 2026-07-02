import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  tone: "blue" | "amber" | "green" | "red";
  icon: LucideIcon;
}

export function StatCard({ label, value, tone, icon: Icon }: StatCardProps) {
  return (
    <div className={`stat-card ${tone}`}>
      <Icon size={22} aria-hidden="true" />
      <div>
        <span>{value}</span>
        <p>{label}</p>
      </div>
    </div>
  );
}
