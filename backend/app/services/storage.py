"""
Investigation Storage Service
-----------------------------
Thread-safe in-memory storage for investigations, tracking lifecycle statuses:
'pending', 'running', 'completed', 'failed'.
"""

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
from threading import Lock

from ..schemas.common import InvestigationStatus, Recommendation
from ..schemas.investigation import InvestigationRecord, InvestigationSummary
from ..schemas.report import InvestigationReport


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower().strip())
    cleaned = re.sub(r"^-+|-+$", "", cleaned)
    return cleaned or "company"


class InvestigationStore:
    def __init__(self):
        self._lock = Lock()
        self._records: Dict[str, InvestigationRecord] = {}

    def create(
        self,
        company_name: str,
        request: str,
        investigation_id: Optional[str] = None,
    ) -> InvestigationRecord:
        with self._lock:
            target_id = investigation_id or slugify(company_name)
            # If target_id already exists, ensure unique slug with count if needed
            counter = 1
            original_id = target_id
            while target_id in self._records and self._records[target_id].status != InvestigationStatus.COMPLETED:
                target_id = f"{original_id}-{counter}"
                counter += 1

            now = utc_now_iso()
            record = InvestigationRecord(
                id=target_id,
                company_name=company_name.strip(),
                request=request.strip(),
                status=InvestigationStatus.PENDING,
                current_step="pending",
                created_at=now,
                updated_at=now,
                report=None,
                error=None,
            )
            self._records[target_id] = record
            return record

    def get(self, investigation_id: str) -> Optional[InvestigationRecord]:
        with self._lock:
            return self._records.get(investigation_id)

    def list(self) -> List[InvestigationRecord]:
        with self._lock:
            return list(self._records.values())

    def list_summaries(self) -> List[InvestigationSummary]:
        with self._lock:
            summaries: List[InvestigationSummary] = []
            for rec in self._records.values():
                if rec.report:
                    summaries.append(
                        InvestigationSummary(
                            id=rec.id,
                            company_name=rec.company_name,
                            sector=rec.report.company.sector,
                            request=rec.request,
                            created_at=rec.created_at,
                            verdict=rec.report.recommendation.verdict,
                            score=rec.report.recommendation.score,
                        )
                    )
                else:
                    summaries.append(
                        InvestigationSummary(
                            id=rec.id,
                            company_name=rec.company_name,
                            sector="Investigation in progress",
                            request=rec.request,
                            created_at=rec.created_at,
                            verdict=Recommendation.PROCEED_WITH_CAUTION,
                            score=0,
                        )
                    )
            return summaries

    def update_status(
        self,
        investigation_id: str,
        status: InvestigationStatus,
        current_step: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[InvestigationRecord]:
        with self._lock:
            record = self._records.get(investigation_id)
            if not record:
                return None
            record.status = status
            if current_step is not None:
                record.current_step = current_step
            if error is not None:
                record.error = error
            record.updated_at = utc_now_iso()
            return record

    def set_report(
        self,
        investigation_id: str,
        report: InvestigationReport,
    ) -> Optional[InvestigationRecord]:
        with self._lock:
            record = self._records.get(investigation_id)
            if not record:
                return None
            record.report = report
            record.status = InvestigationStatus.COMPLETED
            record.current_step = "completed"
            record.updated_at = utc_now_iso()
            record.error = None
            return record


    def seed_initial_investigations(self):
        """Pre-seeds the 3 initial sample records for immediate demo/testing compatibility."""
        from ..schemas.common import ClaimStatus, RiskLevel, Source
        from ..schemas.company import CompanyMetrics, CompanyOverview, Competitor, Founder
        from ..schemas.report import (
            Claim,
            InvestmentMemo,
            KeyFinding,
            MemoSection,
            RecommendationSummary,
            Risk,
        )

        samples = [
            {
                "id": "vectrix-robotics",
                "name": "Vectrix Robotics",
                "sector": "Industrial Automation",
                "stage": "Series B",
                "founded": "2019",
                "hq": "Pittsburgh, PA",
                "tagline": "Autonomous inspection robots for energy infrastructure.",
                "verdict": Recommendation.PROCEED,
                "score": 84,
                "conf": 88,
                "funding": "$46M",
                "round": "Series B · $30M",
                "date": "Jan 2026",
                "val": "$210M (post-money, reported)",
                "emp": 142,
                "growth": "+52% YoY",
                "inv": ["Forgepoint Capital", "Steelhead Partners", "Ironwood VC"],
                "req": "Evaluate for a $5M participation in the Series B extension.",
            },
            {
                "id": "lumora-health",
                "name": "Lumora Health",
                "sector": "HealthTech · AI Diagnostics",
                "stage": "Series A",
                "founded": "2021",
                "hq": "Boston, MA",
                "tagline": "AI-assisted early detection for chronic kidney disease.",
                "verdict": Recommendation.PROCEED_WITH_CAUTION,
                "score": 68,
                "conf": 82,
                "funding": "$18.4M",
                "round": "Series A · $14M",
                "date": "Mar 2026",
                "val": "$72M (post-money, reported)",
                "emp": 64,
                "growth": "+38% YoY",
                "inv": ["Northbridge Ventures", "Halcyon Health Fund", "Atlas Seed"],
                "req": "Analyze this startup for a potential investment of $2M.",
            },
            {
                "id": "quillpay",
                "name": "Quillpay",
                "sector": "FinTech · B2B Payments",
                "stage": "Seed",
                "founded": "2023",
                "hq": "Austin, TX",
                "tagline": "Embedded invoicing and payouts for creator agencies.",
                "verdict": Recommendation.AVOID,
                "score": 34,
                "conf": 76,
                "funding": "$3.2M",
                "round": "Seed · $2.5M",
                "date": "Jun 2025",
                "val": "$14M (post-money, reported)",
                "emp": 11,
                "growth": "-15% YoY",
                "inv": ["Lonestar Angels", "Pinecrest Seed"],
                "req": "Verify traction claims before a $500K angel check.",
            },
        ]

        now = utc_now_iso()
        for item in samples:
            report = InvestigationReport(
                id=item["id"],
                request=item["req"],
                generated_at=now,
                company=CompanyOverview(
                    name=item["name"],
                    tagline=item["tagline"],
                    description=f"{item['name']} operates in {item['sector']}.",
                    sector=item["sector"],
                    stage=item["stage"],
                    founded=item["founded"],
                    headquarters=item["hq"],
                    website=f"https://www.{item['id']}.com",
                    business_model="B2B Subscription / Enterprise Contract",
                ),
                metrics=CompanyMetrics(
                    total_funding=item["funding"],
                    last_round=item["round"],
                    last_round_date=item["date"],
                    valuation=item["val"],
                    employees=item["emp"],
                    employee_growth=item["growth"],
                    investors=item["inv"],
                ),
                founders=[
                    Founder(
                        name="Founder & CEO",
                        role="Chief Executive Officer",
                        background=f"Founding leadership for {item['name']}.",
                        previous_companies=["Prior Tech Venture"],
                        profile_url=f"https://www.linkedin.com/company/{item['id']}",
                    )
                ],
                competitors=[
                    Competitor(
                        name=f"Peer in {item['sector']}",
                        description="Direct sector competitor.",
                        funding="$25M",
                        positioning="Challenger",
                        threat=RiskLevel.medium,
                    )
                ],
                findings=[
                    KeyFinding(
                        title="Sample Ingested",
                        detail=f"Diligence record for {item['name']}.",
                        sentiment="positive" if item["score"] > 70 else "neutral",
                    )
                ],
                risks=[
                    Risk(
                        category="Market",
                        title="Competitive Dynamics",
                        description=f"Rapidly evolving market space in {item['sector']}.",
                        level=RiskLevel.medium,
                        mitigation="Monitor customer acquisition and churn rates.",
                    )
                ],
                claims=[
                    Claim(
                        id=f"{item['id']}-c1",
                        claim=f"{item['name']} primary operating mandate: {item['req']}",
                        status=ClaimStatus.UNVERIFIED,
                        evidence="Sample investigation profile.",
                        source=Source(
                            title=f"{item['name']} profile",
                            url=f"https://www.{item['id']}.com",
                        ),
                    )
                ],
                recommendation=RecommendationSummary(
                    verdict=item["verdict"],
                    score=item["score"],
                    confidence=item["conf"],
                    summary=f"Automated evaluation completed with verdict: {item['verdict']}.",
                    conditions=[
                        "Verify audited financial statements",
                        "Conduct customer reference calls",
                    ],
                ),
                memo=InvestmentMemo(
                    thesis=f"Evaluation of {item['name']} for {item['req']}.",
                    sections=[
                        MemoSection(
                            heading="Opportunity",
                            body=f"Market opportunity in {item['sector']}.",
                        )
                    ],
                ),
            )

            rec = InvestigationRecord(
                id=item["id"],
                company_name=item["name"],
                request=item["req"],
                status=InvestigationStatus.COMPLETED,
                current_step="completed",
                created_at=now,
                updated_at=now,
                report=report,
                error=None,
            )
            self._records[item["id"]] = rec


# Shared storage instance
investigation_store = InvestigationStore()
investigation_store.seed_initial_investigations()

