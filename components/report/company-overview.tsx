import { Building2, ExternalLink } from "lucide-react";
import { SectionCard } from "@/components/report/section-card";
import type { CompanyOverview as CompanyOverviewData } from "@/lib/types";

export function CompanyOverview({ company }: { company: CompanyOverviewData }) {
  const facts = [
    { label: "Sector", value: company.sector },
    { label: "Stage", value: company.stage },
    { label: "Founded", value: company.founded },
    { label: "Headquarters", value: company.headquarters },
    { label: "Business model", value: company.businessModel },
  ];

  return (
    <SectionCard
      id="overview"
      title="Company overview"
      icon={Building2}
      className="lg:col-span-2"
    >
      <p className="mb-2 font-medium text-foreground">{company.tagline}</p>
      <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
        {company.description}
      </p>
      <dl className="grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-3">
        {facts.map((fact) => (
          <div key={fact.label}>
            <dt className="text-xs text-muted-foreground">{fact.label}</dt>
            <dd className="text-sm font-medium text-foreground">
              {fact.value}
            </dd>
          </div>
        ))}
        <div>
          <dt className="text-xs text-muted-foreground">Website</dt>
          <dd>
            {company.website ? (
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm font-medium text-brand hover:underline"
              >
                {company.website.replace(/^https?:\/\/(www\.)?/, "")}
                <ExternalLink className="size-3" aria-hidden="true" />
              </a>
            ) : (
              <span className="text-sm text-muted-foreground">Unavailable</span>
            )}
          </dd>
        </div>
      </dl>
    </SectionCard>
  );
}
