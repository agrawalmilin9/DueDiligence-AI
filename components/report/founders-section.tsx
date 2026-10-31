import { ExternalLink, Users } from "lucide-react";
import { SectionCard } from "@/components/report/section-card";
import type { Founder } from "@/lib/types";

export function FoundersSection({ founders }: { founders: Founder[] }) {
  return (
    <SectionCard
      id="founders"
      title="Founders"
      description="Background and prior experience"
      icon={Users}
    >
      <ul className="grid gap-4 md:grid-cols-3">
        {founders.length === 0 && (
          <li className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground md:col-span-3">
            No founder-title candidates were returned for this company.
          </li>
        )}
        {founders.map((founder) => (
          <li
            key={founder.name}
            className="flex flex-col gap-3 rounded-xl border p-4"
          >
            <div className="flex items-center gap-3">
              <span
                aria-hidden="true"
                className="flex size-11 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground"
              >
                {founder.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </span>
              <div>
                <p className="font-medium text-foreground">{founder.name}</p>
                <p className="text-xs text-muted-foreground">{founder.role}</p>
              </div>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {founder.background}
            </p>
            <div className="mt-auto flex flex-wrap items-center justify-between gap-2">
              <div className="flex flex-wrap gap-1.5">
                {founder.previousCompanies.map((company) => (
                  <span
                    key={company}
                    className="rounded-md bg-secondary px-2 py-0.5 text-xs text-secondary-foreground"
                  >
                    {company}
                  </span>
                ))}
              </div>
              {founder.profileUrl && (
                <a
                  href={founder.profileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-medium text-brand hover:underline"
                >
                  Profile
                  <ExternalLink className="size-3" aria-hidden="true" />
                  <span className="sr-only">for {founder.name}</span>
                </a>
              )}
            </div>
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}
