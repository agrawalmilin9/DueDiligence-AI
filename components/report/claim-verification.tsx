import { BadgeCheck, ExternalLink } from "lucide-react";
import { SectionCard } from "@/components/report/section-card";
import { StatusPill } from "@/components/report/status-pill";
import { claimStatusStyles } from "@/lib/labels";
import type { Claim, ClaimStatus } from "@/lib/types";

const statuses: ClaimStatus[] = [
  "VERIFIED",
  "CONTRADICTED",
  "CONFLICTING",
  "UNVERIFIED",
];

export function ClaimVerification({ claims }: { claims: Claim[] }) {
  return (
    <SectionCard
      id="claims"
      title="Claim verification"
      description="Every claim is checked against an independent source"
      icon={BadgeCheck}
      action={
        <div className="hidden flex-wrap justify-end gap-1.5 sm:flex">
          {statuses.map((status) => (
            <StatusPill key={status} className={claimStatusStyles[status]}>
              {claims.filter((c) => c.status === status).length} {status}
            </StatusPill>
          ))}
        </div>
      }
    >
      <ul className="flex flex-col gap-3">
        {claims.length === 0 && (
          <li className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground">
            No explicit claims were supplied for verification.
          </li>
        )}
        {claims.map((claim) => (
          <li
            key={claim.id}
            className="grid gap-3 rounded-xl border p-4 transition-colors hover:border-brand/30 sm:grid-cols-[1fr_auto]"
          >
            <div className="flex flex-col gap-1.5">
              <p className="text-sm font-medium text-foreground">
                &ldquo;{claim.claim}&rdquo;
              </p>
              <p className="text-sm text-muted-foreground">{claim.evidence}</p>
              {claim.source.url ? (
                <a
                  href={claim.source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex w-fit items-center gap-1.5 text-xs font-medium text-brand hover:underline"
                >
                  <ExternalLink className="size-3" aria-hidden="true" />
                  Source: {claim.source.title}
                </a>
              ) : (
                <span className="text-xs text-muted-foreground">
                  Source unavailable: {claim.source.title}
                </span>
              )}
            </div>
            <div className="sm:pt-0.5">
              <StatusPill className={claimStatusStyles[claim.status]}>
                {claim.status}
              </StatusPill>
            </div>
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}
