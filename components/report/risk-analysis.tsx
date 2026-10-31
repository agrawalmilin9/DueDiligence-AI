import { ShieldAlert } from "lucide-react";
import { SectionCard } from "@/components/report/section-card";
import { StatusPill } from "@/components/report/status-pill";
import { riskLevelStyles } from "@/lib/labels";
import type { Risk, RiskLevel } from "@/lib/types";
import { cn } from "@/lib/utils";

const levels: RiskLevel[] = ["high", "medium", "low"];

const barColor: Record<RiskLevel, string> = {
  high: "bg-destructive",
  medium: "bg-warning",
  low: "bg-success",
};

export function RiskAnalysis({ risks }: { risks: Risk[] }) {
  const counts = levels.map((level) => ({
    level,
    count: risks.filter((r) => r.level === level).length,
  }));

  return (
    <SectionCard id="risks" title="Risk analysis" icon={ShieldAlert}>
      <div className="mb-5">
        <div
          className="flex h-2 overflow-hidden rounded-full bg-muted"
          aria-hidden="true"
        >
          {counts.map(({ level, count }) => (
            <div
              key={level}
              className={barColor[level]}
              style={{
                width: `${risks.length ? (count / risks.length) * 100 : 0}%`,
              }}
            />
          ))}
        </div>
        <p className="mt-2 flex gap-4 text-xs text-muted-foreground">
          {counts.map(({ level, count }) => (
            <span key={level} className="flex items-center gap-1.5 capitalize">
              <span
                className={cn("size-2 rounded-full", barColor[level])}
                aria-hidden="true"
              />
              {count} {level}
            </span>
          ))}
        </p>
      </div>

      <ul className="flex flex-col divide-y">
        {risks.length === 0 && (
          <li className="py-3 text-sm text-muted-foreground">
            No risks were identified from the available evidence.
          </li>
        )}
        {risks.map((risk) => (
          <li key={risk.title} className="py-3 first:pt-0 last:pb-0">
            <div className="mb-1 flex items-center justify-between gap-3">
              <p className="text-sm font-medium text-foreground">
                <span className="text-muted-foreground">
                  {risk.category} ·{" "}
                </span>
                {risk.title}
              </p>
              <StatusPill className={riskLevelStyles[risk.level]}>
                {risk.level}
              </StatusPill>
            </div>
            <p className="text-sm text-muted-foreground">{risk.description}</p>
            <p className="mt-1 text-xs text-accent-foreground">
              <span className="font-medium">Mitigation:</span> {risk.mitigation}
            </p>
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}
