"""Stage 7: produce a rules-based, evidence-qualified investment memo."""

from ..base import BasePipelineStage, PipelineContext
from ...schemas.common import ClaimStatus, Recommendation, RiskLevel
from ...schemas.report import InvestmentMemo, MemoSection, RecommendationSummary


def _source_domains(context):
    domains = set()
    for url in context.extra_data.get("evidence_source_urls", []):
        parts = url.split("/")
        if len(parts) > 2 and parts[2]:
            domains.add(parts[2].lower().removeprefix("www."))
    return domains


def _recommendation(context):
    claim_counts = context.extra_data.get("claim_status_counts", {})
    contradicted = claim_counts.get(ClaimStatus.CONTRADICTED.value, 0)
    verified = claim_counts.get(ClaimStatus.VERIFIED.value, 0)
    high_risks = sum(risk.level == RiskLevel.high for risk in context.risks)
    medium_risks = sum(risk.level == RiskLevel.medium for risk in context.risks)

    if contradicted >= 2:
        verdict = Recommendation.AVOID
        summary = "Avoid pending resolution of multiple claims contradicted on multiple source hosts."
    elif (
        not context.risks
        and context.crustdata_company_id is not None
        and context.founders
        and context.competitors
        and verified > 0
    ):
        verdict = Recommendation.PROCEED
        summary = "Available company, management, market, and claim evidence supports proceeding to full investment diligence."
    else:
        verdict = Recommendation.PROCEED_WITH_CAUTION
        summary = "Evidence is incomplete or includes unresolved risks; do not treat this preliminary report as an investment approval."

    score = max(0, min(100, 75 + 5 * verified - 25 * contradicted - 10 * medium_risks - 25 * high_risks))
    confidence = min(95, 10 + 12 * min(5, len(_source_domains(context))) + (10 if context.crustdata_company_id else 0))
    conditions = list(dict.fromkeys(risk.mitigation for risk in context.risks))
    if not context.claims:
        conditions.append("Provide explicit statements under a Claims: section to verify pitch assertions.")
    if not conditions:
        conditions.append("Complete primary-source financial, legal, and customer diligence before investment.")
    return RecommendationSummary(
        verdict=verdict,
        score=score,
        confidence=confidence,
        summary=summary,
        conditions=conditions,
    )


def _memo_sections(context):
    company = context.company_overview
    metrics = context.metrics
    jobs = (context.extra_data.get("hiring_research") or {}).get("jobs", [])
    job_details = "\n".join(
        f"{job.get('title') or 'Untitled role'} - {job.get('url') or 'URL unavailable'}"
        for job in jobs
        if isinstance(job, dict)
    )
    hiring_summary = (
        f"Indexed job openings: {len(jobs)}.\n{job_details}"
        if jobs
        else "Indexed job openings: none returned; this does not establish that the company is not hiring."
    )
    sections = [
        MemoSection(
            heading="Executive Summary",
            body=context.recommendation.summary,
        ),
        MemoSection(
            heading="Company Profile",
            body=(
                f"{company.name}. Sector: {company.sector}. Founded: {company.founded}. "
                f"Headquarters: {company.headquarters}. Website: {company.website or 'Unavailable'}. "
                f"Business model: {company.business_model}."
            ),
        ),
        MemoSection(
            heading="Financial and Team Signals",
            body=(
                f"Funding: {metrics.total_funding}. Last round: {metrics.last_round} ({metrics.last_round_date}). "
                f"Valuation: {metrics.valuation}. Employees: {metrics.employees}. "
                f"Headcount growth: {metrics.employee_growth}. Investors: "
                f"{', '.join(metrics.investors) if metrics.investors else 'Unavailable'}."
            ),
        ),
        MemoSection(
            heading="Management and Market",
            body=(
                "Founder candidates are inferred from current employment titles and require independent verification. "
                f"Candidates: {', '.join(founder.name for founder in context.founders) if context.founders else 'None returned'}. "
                f"Comparable competitor candidates: {len(context.competitors)}.\n{hiring_summary}"
            ),
        ),
        MemoSection(
            heading="Claim Verification",
            body=(
                "\n".join(
                    f"{claim.status.value}: {claim.claim} Evidence: {claim.evidence} Source: {claim.source.url or 'No source found'}."
                    for claim in context.claims
                )
                if context.claims
                else "No explicit claims were supplied for verification. No claims were invented."
            ),
        ),
        MemoSection(
            heading="Risks and Conditions",
            body=(
                "\n".join(
                    f"{risk.level.value.upper()} - {risk.title}: {risk.description} Mitigation: {risk.mitigation}"
                    for risk in context.risks
                )
                if context.risks
                else "No rule-triggered risks were identified from the available evidence."
            ),
        ),
        MemoSection(
            heading="Sources",
            body=(
                "\n".join(context.extra_data.get("evidence_source_urls", []))
                if context.extra_data.get("evidence_source_urls")
                else "No public source URLs were retrieved."
            ),
        ),
    ]
    return sections


class ReportGeneratorStage(BasePipelineStage):
    @property
    def stage_id(self) -> str:
        return "report"

    @property
    def stage_name(self) -> str:
        return "Preparing investment report"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        context.recommendation = _recommendation(context)
        context.memo = InvestmentMemo(
            thesis=context.recommendation.summary,
            sections=_memo_sections(context),
        )
        return context
