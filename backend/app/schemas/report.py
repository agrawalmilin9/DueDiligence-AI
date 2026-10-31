from typing import List, Literal
from .base import CamelModel
from .common import ClaimStatus, Recommendation, RiskLevel, Source
from .company import CompanyMetrics, CompanyOverview, Competitor, Founder


class KeyFinding(CamelModel):
    title: str
    detail: str
    sentiment: Literal["positive", "neutral", "negative"]


class Risk(CamelModel):
    category: str
    title: str
    description: str
    level: RiskLevel
    mitigation: str


class Claim(CamelModel):
    id: str
    claim: str
    status: ClaimStatus
    evidence: str
    source: Source


class RecommendationSummary(CamelModel):
    verdict: Recommendation
    score: int
    confidence: int
    summary: str
    conditions: List[str]


class MemoSection(CamelModel):
    heading: str
    body: str


class InvestmentMemo(CamelModel):
    thesis: str
    sections: List[MemoSection]


class InvestigationReport(CamelModel):
    id: str
    request: str
    generated_at: str
    company: CompanyOverview
    metrics: CompanyMetrics
    founders: List[Founder]
    competitors: List[Competitor]
    findings: List[KeyFinding]
    risks: List[Risk]
    claims: List[Claim]
    recommendation: RecommendationSummary
    memo: InvestmentMemo
