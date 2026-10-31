"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Check, CircleAlert, Loader2, Sparkles } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  getApiErrorMessage,
  getInvestigation,
  investigationSteps,
} from "@/lib/investigations";
import type { InvestigationStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const POLL_INTERVAL_MS = 1500;
const POLL_TIMEOUT_MS = 10 * 60 * 1000;

export function InvestigationProgress({
  companyName,
  investigationId,
  request,
}: {
  companyName: string;
  investigationId: string;
  request: string;
}) {
  const router = useRouter();
  const [status, setStatus] = useState<InvestigationStatus>("pending");
  const [currentStep, setCurrentStep] = useState<string | null>("starting");
  const [error, setError] = useState("");
  const total = investigationSteps.length;
  const isDone = status === "completed";
  const isFailed = status === "failed";
  const foundStep = investigationSteps.findIndex(
    (step) => step.id === currentStep,
  );
  const activeIndex = foundStep >= 0 ? foundStep : 0;
  const completed = isDone ? total : activeIndex;
  const percent = Math.round((completed / total) * 100);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function pollInvestigation() {
      const deadline = Date.now() + POLL_TIMEOUT_MS;
      while (!cancelled) {
        try {
          const investigation = await getInvestigation(investigationId);
          if (cancelled) return;
          setStatus(investigation.status);
          setCurrentStep(investigation.currentStep);
          if (investigation.status === "failed") {
            setError(
              investigation.error ||
                "The investigation failed before a report was produced.",
            );
            return;
          }
          if (investigation.status === "completed") {
            router.replace(`/report/${encodeURIComponent(investigationId)}`);
            return;
          }
        } catch (pollError) {
          if (!cancelled) {
            setStatus("failed");
            setError(getApiErrorMessage(pollError));
          }
          return;
        }

        if (Date.now() >= deadline) {
          setStatus("failed");
          setError(
            "This investigation is taking longer than expected. Return to the dashboard and try again later.",
          );
          return;
        }
        await new Promise<void>((resolve) => {
          timer = setTimeout(resolve, POLL_INTERVAL_MS);
        });
      }
    }

    void pollInvestigation();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [investigationId, router]);

  const currentLabel = isFailed
    ? "Investigation failed"
    : isDone
      ? "Report ready"
      : investigationSteps[activeIndex].label;

  return (
    <div className="animate-in fade-in zoom-in-95 duration-500">
      <div className="mb-8 flex flex-col items-center gap-4 text-center">
        <div className="relative flex size-16 items-center justify-center">
          <span
            className="absolute inset-0 animate-ping rounded-full bg-brand/15"
            aria-hidden="true"
          />
          <span className="relative flex size-14 items-center justify-center rounded-full bg-primary text-primary-foreground">
            <Sparkles className="size-6" aria-hidden="true" />
          </span>
        </div>
        <div>
          <p className="text-sm font-medium text-brand">
            Investigation in progress
          </p>
          <h1 className="text-balance text-3xl font-semibold tracking-tight text-primary">
            {companyName}
          </h1>
          <p className="mx-auto mt-2 max-w-md text-pretty text-sm text-muted-foreground">
            {request}
          </p>
        </div>
      </div>

      <div className="rounded-2xl border bg-card p-5 shadow-sm sm:p-6">
        <div className="mb-5 flex flex-col gap-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-foreground">{currentLabel}</span>
            <span
              className="font-mono text-muted-foreground"
              aria-hidden="true"
            >
              {percent}%
            </span>
          </div>
          <Progress
            value={percent}
            aria-label="Investigation progress"
            className="[&_[data-slot=progress-track]]:h-2 [&_[data-slot=progress-indicator]]:bg-brand [&_[data-slot=progress-indicator]]:duration-700"
          />
        </div>

        <ol className="flex flex-col gap-1" aria-live="polite">
          {investigationSteps.map((step, index) => {
            const state =
              index < completed
                ? "done"
                : index === activeIndex && !isDone
                  ? isFailed
                    ? "failed"
                    : "active"
                  : "pending";
            return (
              <li
                key={step.id}
                className={cn(
                  "flex items-start gap-3 rounded-lg px-3 py-2.5 transition-colors duration-300",
                  state === "active" && "bg-accent",
                )}
              >
                <span
                  className={cn(
                    "mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full border transition-all duration-300",
                    state === "done" &&
                      "border-success bg-success text-primary-foreground",
                    state === "active" && "border-brand bg-card text-brand",
                    state === "failed" &&
                      "border-destructive bg-card text-destructive",
                    state === "pending" &&
                      "border-border bg-card text-muted-foreground",
                  )}
                >
                  {state === "done" ? (
                    <Check
                      className="size-3.5 animate-in zoom-in"
                      aria-hidden="true"
                    />
                  ) : state === "failed" ? (
                    <CircleAlert className="size-3.5" aria-hidden="true" />
                  ) : state === "active" ? (
                    <Loader2
                      className="size-3.5 animate-spin"
                      aria-hidden="true"
                    />
                  ) : (
                    <span className="text-[10px] font-medium">{index + 1}</span>
                  )}
                </span>
                <div className="min-w-0">
                  <p
                    className={cn(
                      "text-sm font-medium",
                      state === "pending"
                        ? "text-muted-foreground"
                        : "text-foreground",
                    )}
                  >
                    {step.label}
                    <span className="sr-only">
                      {state === "done"
                        ? " — complete"
                        : state === "failed"
                          ? " — failed"
                          : state === "active"
                            ? " — in progress"
                            : " — pending"}
                    </span>
                  </p>
                  {state !== "pending" && (
                    <p className="text-xs text-muted-foreground animate-in fade-in">
                      {step.detail}
                    </p>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      </div>

      {error && (
        <p
          role="alert"
          className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
        >
          {error}
        </p>
      )}

      <div className="mt-6 text-center">
        <Link
          href="/"
          className={buttonVariants({ variant: "ghost", size: "sm" })}
        >
          Cancel investigation
        </Link>
      </div>
    </div>
  );
}
