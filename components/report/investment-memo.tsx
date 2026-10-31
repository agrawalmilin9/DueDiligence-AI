import { FileText } from "lucide-react";
import { SectionCard } from "@/components/report/section-card";
import type { InvestmentMemo as InvestmentMemoData } from "@/lib/types";

export function InvestmentMemo({
  memo,
  request,
}: {
  memo: InvestmentMemoData;
  request: string;
}) {
  return (
    <SectionCard
      id="memo"
      title="Investment memo"
      description={request}
      icon={FileText}
    >
      <blockquote className="mb-6 border-l-2 border-brand bg-accent/50 py-3 pr-3 pl-4 text-sm leading-relaxed text-accent-foreground">
        <span className="mb-1 block text-xs font-semibold tracking-wider uppercase">
          Thesis
        </span>
        {memo.thesis}
      </blockquote>
      <div className="grid gap-6 md:grid-cols-2">
        {memo.sections.map((section) => (
          <article key={section.heading}>
            <h3 className="mb-1.5 text-sm font-semibold text-primary">
              {section.heading}
            </h3>
            <p className="break-words text-sm leading-relaxed whitespace-pre-line text-muted-foreground">
              {section.body}
            </p>
          </article>
        ))}
      </div>
    </SectionCard>
  );
}
