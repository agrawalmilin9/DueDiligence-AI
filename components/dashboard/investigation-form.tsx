"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowRight, Building2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  createInvestigation,
  DEFAULT_REQUEST,
  getApiErrorMessage,
} from "@/lib/investigations";

const EXAMPLE_REQUESTS = [
  "Analyze this startup for a potential investment of $2M",
  "Verify revenue and customer claims from the pitch deck",
  "Assess founder backgrounds and competitive risks",
];

export function InvestigationForm() {
  const router = useRouter();
  const [company, setCompany] = useState("");
  const [request, setRequest] = useState("");
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState("");

  const canSubmit = company.trim().length > 1 && !isPending;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;
    setError("");
    setIsPending(true);
    const normalizedCompany = company.trim();
    const normalizedRequest = request.trim() || DEFAULT_REQUEST;
    try {
      const investigation = await createInvestigation(
        normalizedCompany,
        normalizedRequest,
      );
      const params = new URLSearchParams({
        id: investigation.id,
        company: investigation.companyName,
        request: investigation.request,
      });
      router.push(`/investigate?${params.toString()}`);
    } catch (submissionError) {
      setError(getApiErrorMessage(submissionError));
      setIsPending(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border bg-card p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_12px_32px_-12px_rgba(30,58,138,0.18)] sm:p-7"
    >
      <div className="flex flex-col gap-5">
        <div className="flex flex-col gap-2">
          <Label htmlFor="company" className="text-sm font-medium">
            Startup name
          </Label>
          <div className="relative">
            <Building2
              className="pointer-events-none absolute top-1/2 left-4 size-5 -translate-y-1/2 text-muted-foreground"
              aria-hidden="true"
            />
            <Input
              id="company"
              name="company"
              autoComplete="off"
              placeholder="e.g. Lumora Health"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="h-14 rounded-xl pl-12 text-base md:text-lg"
              required
            />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="request" className="text-sm font-medium">
            Investigation request
          </Label>
          <Textarea
            id="request"
            name="request"
            placeholder="Analyze this startup for a potential investment of $2M"
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            className="min-h-28 resize-none rounded-xl text-base"
          />
          <div className="flex flex-wrap gap-2 pt-1">
            {EXAMPLE_REQUESTS.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setRequest(example)}
                className="rounded-full border bg-secondary/60 px-3 py-1 text-xs text-secondary-foreground transition-colors hover:border-brand/40 hover:bg-accent"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}

        <Button
          type="submit"
          size="lg"
          disabled={!canSubmit}
          className="h-12 rounded-xl text-base"
        >
          {isPending ? (
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
          ) : null}
          Start Investigation
          {!isPending && <ArrowRight className="size-4" aria-hidden="true" />}
        </Button>
      </div>
    </form>
  );
}
