import type {
  InvestigationRecord,
  InvestigationReport,
  InvestigationSummary,
} from "./types";

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export class BackendApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "BackendApiError";
  }
}

async function fetchBackend<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      cache: "no-store",
    });
  } catch {
    throw new BackendApiError(
      `Could not connect to the backend at ${API_BASE_URL}.`,
    );
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const detail =
      payload &&
      typeof payload === "object" &&
      "detail" in payload &&
      typeof payload.detail === "string"
        ? payload.detail
        : `Backend request failed with status ${response.status}.`;
    throw new BackendApiError(detail, response.status);
  }

  if (payload === null) {
    throw new BackendApiError("The backend returned an empty response.");
  }
  return payload as T;
}

export function getApiErrorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "An unexpected backend error occurred.";
}

export const DEFAULT_REQUEST =
  "Analyze this startup for a potential investment of $2M.";

export function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function titleFromSlug(slug: string) {
  return slug
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export async function createInvestigation(
  companyName: string,
  request: string,
): Promise<InvestigationRecord> {
  return fetchBackend<InvestigationRecord>("/investigations?sync=false", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ companyName, request }),
  });
}

export async function getRecentInvestigations(): Promise<
  InvestigationSummary[]
> {
  return fetchBackend<InvestigationSummary[]>("/investigations");
}

export async function getInvestigation(
  id: string,
): Promise<InvestigationRecord> {
  return fetchBackend<InvestigationRecord>(
    `/investigations/${encodeURIComponent(id)}`,
  );
}

export async function getInvestigationReport(
  id: string,
): Promise<InvestigationReport> {
  return fetchBackend<InvestigationReport>(
    `/investigations/${encodeURIComponent(id)}/report`,
  );
}

export const investigationSteps = [
  {
    id: "identify",
    label: "Identifying company",
    detail: "Resolving legal entity, domain, and registry records",
  },
  {
    id: "company_info",
    label: "Retrieving company information",
    detail: "Loading funding, headcount, and company profile data",
  },
  {
    id: "founders",
    label: "Researching founders",
    detail: "Cross-referencing professional history and prior ventures",
  },
  {
    id: "market",
    label: "Analyzing market and competitors",
    detail: "Mapping competitive landscape and funding activity",
  },
  {
    id: "claims",
    label: "Verifying claims",
    detail: "Checking statements against filings, press, and public data",
  },
  {
    id: "risks",
    label: "Identifying risks",
    detail: "Scoring financial, market, team, and legal exposure",
  },
  {
    id: "report",
    label: "Preparing investment report",
    detail: "Drafting recommendation and investment memo",
  },
] as const;
