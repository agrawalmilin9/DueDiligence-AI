import { Lightbulb, MinusCircle, ThumbsDown, ThumbsUp } from "lucide-react";
import { SectionCard } from "@/components/report/section-card";
import type { KeyFinding } from "@/lib/types";
import { cn } from "@/lib/utils";

const sentimentConfig = {
  positive: {
    icon: ThumbsUp,
    className: "bg-success/10 text-success",
    label: "Positive",
  },
  neutral: {
    icon: MinusCircle,
    className: "bg-muted text-muted-foreground",
    label: "Neutral",
  },
  negative: {
    icon: ThumbsDown,
    className: "bg-destructive/10 text-destructive",
    label: "Negative",
  },
} as const;

export function KeyFindings({ findings }: { findings: KeyFinding[] }) {
  return (
    <SectionCard id="findings" title="Key findings" icon={Lightbulb}>
      <ul className="flex flex-col gap-4">
        {findings.length === 0 && (
          <li className="text-sm text-muted-foreground">
            No findings were available for this investigation.
          </li>
        )}
        {findings.map((finding) => {
          const config = sentimentConfig[finding.sentiment];
          const Icon = config.icon;
          return (
            <li key={finding.title} className="flex gap-3">
              <span
                className={cn(
                  "flex size-7 shrink-0 items-center justify-center rounded-full",
                  config.className,
                )}
              >
                <Icon className="size-3.5" aria-hidden="true" />
                <span className="sr-only">{config.label}</span>
              </span>
              <div>
                <p className="text-sm font-medium text-foreground">
                  {finding.title}
                </p>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {finding.detail}
                </p>
              </div>
            </li>
          );
        })}
      </ul>
    </SectionCard>
  );
}
