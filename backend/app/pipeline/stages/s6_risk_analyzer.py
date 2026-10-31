"""Stage 6: derive diligence risks and findings from gathered evidence."""

from ..base import BasePipelineStage, PipelineContext
from ...schemas.common import ClaimStatus, RiskLevel
from ...schemas.report import KeyFinding, Risk


UNAVAILABLE = "Not available from Crustdata"


def _source_urls(context):
    urls = []
    market = context.extra_data.get("market_research") or {}
    for source in market.get("sources", []):
        if isinstance(source, dict) and isinstance(source.get("url"), str) and source["url"].startswith("http"):
            urls.append(source["url"])
    for claim in context.claims:
        if claim.source.url.startswith("http"):
            urls.append(claim.source.url)
    for job in (context.extra_data.get("hiring_research") or {}).get("jobs", []):
        if isinstance(job, dict) and isinstance(job.get("url"), str) and job["url"].startswith("http"):
            urls.append(job["url"])
    return list(dict.fromkeys(urls))


class RiskAnalyzerStage(BasePipelineStage):
    @property
    def stage_id(self) -> str:
        return "risks"

    @property
    def stage_name(self) -> str:
        return "Identifying risks"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        context.findings = []
        context.risks = []
        sources = _source_urls(context)
        source_domains = {url.split("/")[2].lower().removeprefix("www.") for url in sources}
        metrics = context.metrics
        hiring = context.extra_data.get("hiring_research") or {}

        if context.crustdata_company_id is not None:
            context.findings.append(
                KeyFinding(
                    title="Company identity matched",
                    detail=(
                        f"Crustdata identified {context.company_overview.name if context.company_overview else context.company_name} "
                        f"as company ID {context.crustdata_company_id}. Matched domain: "
                        f"{context.matched_domain or 'unavailable'}."
                    ),
                    sentiment="neutral",
                )
            )
        else:
            context.risks.append(
                Risk(
                    category="Identity",
                    title="Company identity is unverified",
                    description="No unique, sufficiently confident Crustdata company match was available.",
                    level=RiskLevel.high,
                    mitigation="Confirm the legal entity and primary domain before relying on this report.",
                )
            )

        if context.founders:
            names = ", ".join(founder.name for founder in context.founders)
            context.findings.append(
                KeyFinding(
                    title="Potential founders identified",
                    detail=f"Title-based founder candidates: {names}. Founder status remains inferred, not independently verified.",
                    sentiment="neutral",
                )
            )
        else:
            founder_status = context.extra_data.get("founder_research_status")
            founder_description = (
                "Founder-title candidates were not returned by the indexed people data; this does not establish that the company has no founders."
                if founder_status == "completed"
                else "Founder research could not return candidate data for this investigation."
            )
            context.risks.append(
                Risk(
                    category="Management",
                    title="Founder history is unverified",
                    description=founder_description,
                    level=RiskLevel.medium,
                    mitigation="Confirm founder identities, roles, and prior employment directly.",
                )
            )

        if metrics and metrics.employees != UNAVAILABLE:
            context.findings.append(
                KeyFinding(
                    title="Reported team size",
                    detail=f"Crustdata reports {metrics.employees} employees; this is a database figure, not an audited count.",
                    sentiment="neutral",
                )
            )
        else:
            context.risks.append(
                Risk(
                    category="Company Data",
                    title="Team size is unavailable",
                    description="No usable headcount value was returned by company enrichment.",
                    level=RiskLevel.medium,
                    mitigation="Confirm current employee count and team composition with the company.",
                )
            )

        if hiring.get("jobs"):
            context.findings.append(
                KeyFinding(
                    title="Indexed hiring activity",
                    detail=f"Job search returned {len(hiring['jobs'])} indexed openings. This is a point-in-time dataset, not a complete hiring plan.",
                    sentiment="neutral",
                )
            )
        else:
            hiring_description = (
                f"Job search could not be completed: {hiring['error']}"
                if hiring.get("error")
                else "Job search returned no indexed openings; this does not establish that the company is not hiring."
            )
            context.risks.append(
                Risk(
                    category="Hiring",
                    title="Hiring activity is unverified",
                    description=hiring_description,
                    level=RiskLevel.medium,
                    mitigation="Confirm current roles and hiring plans with the company.",
                )
            )

        if context.competitors:
            context.findings.append(
                KeyFinding(
                    title="Competitor candidates compared",
                    detail=(
                        f"{len(context.competitors)} Crustdata-listed competitor candidates had comparable size data. "
                        "Positioning is inferred from relative headcount or total funding, not market share."
                    ),
                    sentiment="neutral",
                )
            )
        else:
            context.risks.append(
                Risk(
                    category="Market",
                    title="Competitive position is unverified",
                    description="No comparable competitor profile was returned. This is a data coverage gap, not evidence that competitors are absent.",
                    level=RiskLevel.medium,
                    mitigation="Validate the competitor set and compare product, customer, and market-share evidence.",
                )
            )

        status_counts = {status: sum(claim.status == status for claim in context.claims) for status in ClaimStatus}
        if status_counts[ClaimStatus.CONTRADICTED]:
            context.risks.append(
                Risk(
                    category="Claims",
                    title="Claims contradicted on multiple source hosts",
                    description=f"{status_counts[ClaimStatus.CONTRADICTED]} explicit claim(s) were contradicted on at least two source hosts.",
                    level=RiskLevel.high,
                    mitigation="Request primary documentation and resolve each contradiction before investment.",
                )
            )
        if status_counts[ClaimStatus.CONFLICTING]:
            context.risks.append(
                Risk(
                    category="Claims",
                    title="Conflicting public evidence",
                    description=f"{status_counts[ClaimStatus.CONFLICTING]} explicit claim(s) had both supporting and contradicting sources.",
                    level=RiskLevel.medium,
                    mitigation="Reconcile conflicting reports against primary records.",
                )
            )
        if status_counts[ClaimStatus.UNVERIFIED]:
            context.risks.append(
                Risk(
                    category="Claims",
                    title="Some claims remain unverified",
                    description=f"{status_counts[ClaimStatus.UNVERIFIED]} explicit claim(s) lacked matching text on two distinct source hosts.",
                    level=RiskLevel.medium,
                    mitigation="Obtain source documents or independent corroboration for the claims.",
                )
            )

        if sources:
            context.findings.append(
                KeyFinding(
                    title="Public sources collected",
                    detail=f"Collected {len(sources)} source URLs across {len(source_domains)} host domains for review.",
                    sentiment="neutral",
                )
            )
        else:
            context.risks.append(
                Risk(
                    category="Evidence",
                    title="No public source pages were retrieved",
                    description="The web search or page-fetch stage produced no usable source URLs.",
                    level=RiskLevel.medium,
                    mitigation="Repeat research with company-provided URLs and primary documents.",
                )
            )

        headcount_growth = (context.extra_data.get("company_enrichment") or {}).get("headcount", {}).get("growth_percent") or {}
        yoy_growth = headcount_growth.get("yoy") if isinstance(headcount_growth, dict) else None
        if isinstance(yoy_growth, (int, float)) and yoy_growth < 0:
            context.risks.append(
                Risk(
                    category="Operations",
                    title="Reported headcount contraction",
                    description=f"Crustdata reports year-over-year headcount growth of {yoy_growth:.1f}%; this is a signal to investigate, not proof of distress.",
                    level=RiskLevel.medium,
                    mitigation="Review hiring, attrition, and restructuring context with management.",
                )
            )

        context.extra_data["evidence_source_urls"] = sources
        context.extra_data["claim_status_counts"] = {
            status.value: count for status, count in status_counts.items()
        }
        return context
