export type ClaimStatus =
  | "VERIFIED"
  | "CONTRADICTED"
  | "UNVERIFIED"
  | "CONFLICTING";

export type Recommendation = "PROCEED" | "PROCEED_WITH_CAUTION" | "AVOID";

export type RiskLevel = "low" | "medium" | "high";

export type InvestigationStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed";

export interface Source {
  title: string;
  url: string;
}

export interface CompanyOverview {
  name: string;
  tagline: string;
  description: string;
  sector: string;
  stage: string;
  founded: string;
  headquarters: string;
  website: string;
  businessModel: string;
}

export interface CompanyMetrics {
  totalFunding: string;
  lastRound: string;
  lastRoundDate: string;
  valuation: string;
  employees: number | string;
  employeeGrowth: string;
  investors: string[];
}

export interface Founder {
  name: string;
  role: string;
  background: string;
  previousCompanies: string[];
  profileUrl: string;
}

export interface Competitor {
  name: string;
  description: string;
  funding: string;
  positioning: "Leader" | "Challenger" | "Niche";
  threat: RiskLevel;
}

export interface KeyFinding {
  title: string;
  detail: string;
  sentiment: "positive" | "neutral" | "negative";
}

export interface Risk {
  category: string;
  title: string;
  description: string;
  level: RiskLevel;
  mitigation: string;
}

export interface Claim {
  id: string;
  claim: string;
  status: ClaimStatus;
  evidence: string;
  source: Source;
}

export interface RecommendationSummary {
  verdict: Recommendation;
  score: number;
  confidence: number;
  summary: string;
  conditions: string[];
}

export interface InvestmentMemo {
  thesis: string;
  sections: { heading: string; body: string }[];
}

export interface InvestigationReport {
  id: string;
  request: string;
  generatedAt: string;
  company: CompanyOverview;
  metrics: CompanyMetrics;
  founders: Founder[];
  competitors: Competitor[];
  findings: KeyFinding[];
  risks: Risk[];
  claims: Claim[];
  recommendation: RecommendationSummary;
  memo: InvestmentMemo;
}

export interface InvestigationSummary {
  id: string;
  companyName: string;
  sector: string;
  request: string;
  createdAt: string;
  verdict: Recommendation;
  score: number;
}

export interface InvestigationRecord {
  id: string;
  companyName: string;
  request: string;
  status: InvestigationStatus;
  currentStep: string | null;
  createdAt: string;
  updatedAt: string;
  report: InvestigationReport | null;
  error: string | null;
}
