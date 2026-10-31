import { Swords } from "lucide-react";
import { SectionCard } from "@/components/report/section-card";
import { StatusPill } from "@/components/report/status-pill";
import { riskLevelStyles } from "@/lib/labels";
import type { Competitor } from "@/lib/types";

export function CompetitorAnalysis({
  competitors,
}: {
  competitors: Competitor[];
}) {
  return (
    <SectionCard
      id="competitors"
      title="Competitor analysis"
      description="Landscape and threat level"
      icon={Swords}
    >
      <div className="-mx-5 overflow-x-auto sm:-mx-6">
        <table className="w-full min-w-[560px] text-left text-sm">
          <thead>
            <tr className="border-y bg-muted/50 text-xs text-muted-foreground">
              <th scope="col" className="px-5 py-2.5 font-medium sm:px-6">
                Company
              </th>
              <th scope="col" className="px-3 py-2.5 font-medium">
                Positioning
              </th>
              <th scope="col" className="px-3 py-2.5 font-medium">
                Funding
              </th>
              <th
                scope="col"
                className="px-5 py-2.5 text-right font-medium sm:px-6"
              >
                Threat
              </th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {competitors.length === 0 && (
              <tr>
                <td
                  colSpan={4}
                  className="px-5 py-4 text-sm text-muted-foreground sm:px-6"
                >
                  No comparable competitor profiles were available.
                </td>
              </tr>
            )}
            {competitors.map((competitor) => (
              <tr
                key={competitor.name}
                className="transition-colors hover:bg-muted/40"
              >
                <td className="px-5 py-3 sm:px-6">
                  <p className="font-medium text-foreground">
                    {competitor.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {competitor.description}
                  </p>
                </td>
                <td className="px-3 py-3 text-foreground">
                  {competitor.positioning}
                </td>
                <td className="px-3 py-3 font-mono text-foreground">
                  {competitor.funding}
                </td>
                <td className="px-5 py-3 text-right sm:px-6">
                  <StatusPill className={riskLevelStyles[competitor.threat]}>
                    {competitor.threat}
                  </StatusPill>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}
