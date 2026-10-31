import type { Metadata } from "next";
import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { ClaimVerification } from "@/components/report/claim-verification";
import { CompanyOverview } from "@/components/report/company-overview";
import { CompetitorAnalysis } from "@/components/report/competitor-analysis";
import { FoundersSection } from "@/components/report/founders-section";
import { FundingMetrics } from "@/components/report/funding-metrics";
import { InvestmentMemo } from "@/components/report/investment-memo";
import { KeyFindings } from "@/components/report/key-findings";
import { RecommendationCard } from "@/components/report/recommendation-card";
import { ReportHeader } from "@/components/report/report-header";
import { RiskAnalysis } from "@/components/report/risk-analysis";
import {
  BackendApiError,
  getApiErrorMessage,
  getInvestigationReport,
  titleFromSlug,
} from "@/lib/investigations";
import type { InvestigationReport } from "@/lib/types";
import { cn } from "@/lib/utils";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  return {
    title: `${titleFromSlug(id)} — Due Diligence Report | DueDiligence AI`,
  };
}

export default async function ReportPage({ params }: Props) {
  const { id } = await params;
  let report: InvestigationReport;
  try {
    report = await getInvestigationReport(id);
  } catch (error) {
    const title =
      error instanceof BackendApiError && error.status === 404
        ? "Investigation not found"
        : error instanceof BackendApiError && error.status === 409
          ? "Report is not ready yet"
          : "Report unavailable";
    return (
      <main className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-3xl flex-col justify-center px-4 py-12 sm:px-6">
        <section
          role="alert"
          className="rounded-xl border bg-card p-6 shadow-sm sm:p-8"
        >
          <h1 className="text-xl font-semibold text-primary">{title}</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {getApiErrorMessage(error)}
          </p>
          <Link
            href="/"
            className={cn(buttonVariants({ variant: "outline" }), "mt-5")}
          >
            Back to dashboard
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-6 px-4 pt-8 pb-20 sm:px-6">
      <ReportHeader report={report} />
      <RecommendationCard recommendation={report.recommendation} />
      <div className="grid gap-6 lg:grid-cols-3">
        <CompanyOverview company={report.company} />
        <FundingMetrics metrics={report.metrics} />
      </div>
      <FoundersSection founders={report.founders} />
      <div className="grid gap-6 lg:grid-cols-2">
        <KeyFindings findings={report.findings} />
        <RiskAnalysis risks={report.risks} />
      </div>
      <ClaimVerification claims={report.claims} />
      <CompetitorAnalysis competitors={report.competitors} />
      <InvestmentMemo memo={report.memo} request={report.request} />
    </main>
  );
}
