import { FileCheck2, ShieldAlert, Users } from "lucide-react";
import { InvestigationForm } from "@/components/dashboard/investigation-form";
import { RecentInvestigations } from "@/components/dashboard/recent-investigations";
import {
  getApiErrorMessage,
  getRecentInvestigations,
} from "@/lib/investigations";
import type { InvestigationSummary } from "@/lib/types";

const highlights = [
  { icon: Users, label: "Founder background checks" },
  { icon: FileCheck2, label: "Source-linked claim verification" },
  { icon: ShieldAlert, label: "Risk scoring & recommendation" },
];

export default async function DashboardPage() {
  let recent: InvestigationSummary[] = [];
  let recentError = "";
  try {
    recent = await getRecentInvestigations();
  } catch (error) {
    recentError = getApiErrorMessage(error);
  }

  return (
    <main className="relative overflow-hidden">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[520px] bg-[radial-gradient(60%_60%_at_50%_0%,oklch(0.93_0.05_255)_0%,transparent_70%)]"
      />
      <div className="mx-auto flex max-w-6xl flex-col gap-16 px-4 pt-14 pb-20 sm:px-6 sm:pt-20">
        <section
          id="new"
          aria-labelledby="hero-heading"
          className="mx-auto w-full max-w-2xl scroll-mt-24"
        >
          <div className="mb-8 flex flex-col items-center gap-4 text-center animate-in fade-in slide-in-from-bottom-3 duration-700">
            <span className="inline-flex items-center gap-2 rounded-full border bg-card px-3 py-1 text-xs font-medium text-accent-foreground">
              <span
                className="size-1.5 rounded-full bg-brand"
                aria-hidden="true"
              />
              Investment research, automated
            </span>
            <h1
              id="hero-heading"
              className="text-balance text-4xl font-semibold tracking-tight text-primary sm:text-5xl"
            >
              AI-powered Startup Intelligence
            </h1>
            <p className="text-pretty text-lg text-muted-foreground">
              Research startups. Verify claims. Make smarter decisions.
            </p>
          </div>

          <div className="animate-in fade-in slide-in-from-bottom-4 fill-mode-both delay-150 duration-700">
            <InvestigationForm />
          </div>

          <ul className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
            {highlights.map(({ icon: Icon, label }) => (
              <li key={label} className="flex items-center gap-2">
                <Icon className="size-4 text-brand" aria-hidden="true" />
                {label}
              </li>
            ))}
          </ul>
        </section>

        {recentError && (
          <p
            role="alert"
            className="-mt-12 text-center text-sm text-destructive"
          >
            Recent investigations could not be loaded. {recentError}
          </p>
        )}
        <RecentInvestigations items={recent} />
      </div>
    </main>
  );
}
