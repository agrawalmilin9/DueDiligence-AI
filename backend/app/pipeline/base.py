from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..schemas.company import CompanyMetrics, CompanyOverview, Competitor, Founder
from ..schemas.report import (
    Claim,
    InvestmentMemo,
    InvestigationReport,
    KeyFinding,
    RecommendationSummary,
    Risk,
)


@dataclass
class PipelineContext:
    investigation_id: str
    company_name: str
    request: str
    crustdata_company_id: Optional[int] = None
    matched_domain: Optional[str] = None
    company_overview: Optional[CompanyOverview] = None
    metrics: Optional[CompanyMetrics] = None
    founders: List[Founder] = field(default_factory=list)
    competitors: List[Competitor] = field(default_factory=list)
    findings: List[KeyFinding] = field(default_factory=list)
    risks: List[Risk] = field(default_factory=list)
    claims: List[Claim] = field(default_factory=list)
    recommendation: Optional[RecommendationSummary] = None
    memo: Optional[InvestmentMemo] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_report(self, generated_at: str) -> InvestigationReport:
        if not self.company_overview or not self.metrics or not self.recommendation or not self.memo:
            raise ValueError("Pipeline incomplete: required report sections are missing")

        return InvestigationReport(
            id=self.investigation_id,
            request=self.request,
            generated_at=generated_at,
            company=self.company_overview,
            metrics=self.metrics,
            founders=self.founders,
            competitors=self.competitors,
            findings=self.findings,
            risks=self.risks,
            claims=self.claims,
            recommendation=self.recommendation,
            memo=self.memo,
        )


class BasePipelineStage(ABC):
    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Unique slug identifier matching frontend progress steps (e.g. identify, founders, etc.)"""
        pass

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Human readable title for progress tracking"""
        pass

    @abstractmethod
    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute stage logic and mutate/return the context"""
        pass
