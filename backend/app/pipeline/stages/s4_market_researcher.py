"""Stage 4: collect competitor profiles, hiring signals, and public web sources."""

from urllib.parse import urlparse

from ..base import BasePipelineStage, PipelineContext
from ...schemas.common import RiskLevel
from ...schemas.company import Competitor
from ...services.crustdata import CrustdataServiceError, crustdata_service, flatten_company_matches
from ...services.research import research_service


UNAVAILABLE = "Not available from Crustdata"


def _domain(value):
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = (parsed.hostname or "").lower().removeprefix("www.")
    return host or None


def _number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _money(value):
    amount = _number(value)
    if amount is None:
        return UNAVAILABLE
    return f"${amount:,.0f}" if float(amount).is_integer() else f"${amount:,.2f}"


def _positioning(peer_size, target_size):
    if peer_size is None or target_size is None or target_size <= 0:
        return None
    return "Challenger", RiskLevel.medium


class MarketResearcherStage(BasePipelineStage):
    @property
    def stage_id(self) -> str:
        return "market"

    @property
    def stage_name(self) -> str:
        return "Analyzing market and competitors"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        context.competitors = []
        context.extra_data["hiring_research"] = {"jobs": [], "openings_count": None}
        context.extra_data["market_research"] = {"sources": [], "competitor_domains": []}
        if context.crustdata_company_id is None:
            return context

        company_data = context.extra_data.get("company_enrichment") or {}
        hiring = company_data.get("hiring") or {}
        context.extra_data["hiring_research"]["openings_count"] = hiring.get("openings_count")
        context.extra_data["hiring_research"]["openings_growth_percent"] = hiring.get(
            "openings_growth_percent"
        )
        context.extra_data["hiring_research"]["recent_titles_csv"] = hiring.get("recent_titles_csv")

        try:
            jobs_response = await crustdata_service.search_jobs(context.crustdata_company_id)
            jobs = jobs_response.get("job_listings", [])
        except CrustdataServiceError as exc:
            jobs = []
            context.extra_data["hiring_research"]["error"] = str(exc)
        context.extra_data["hiring_research"]["jobs"] = [
            {
                "title": (job.get("job_details") or {}).get("title"),
                "url": (job.get("job_details") or {}).get("url"),
                "workplace_type": (job.get("job_details") or {}).get("workplace_type"),
                "location": (job.get("location") or {}).get("raw"),
                "date_added": (job.get("metadata") or {}).get("date_added"),
            }
            for job in jobs[:20]
            if isinstance(job, dict)
        ]

        competitor_group = company_data.get("competitors") or {}
        target_domain = _domain(context.matched_domain)
        domains = competitor_group.get("all_domains") or []
        if not isinstance(domains, list):
            domains = []
        domains = list(dict.fromkeys(
            domain for value in domains[:10]
            if (domain := _domain(value)) and domain != target_domain
        ))[:3]
        context.extra_data["market_research"]["competitor_domains"] = domains

        peer_profiles = {}
        if domains:
            try:
                response = await crustdata_service.enrich_competitors(domains)
                for result in response:
                    result_domain = _domain(result.get("matched_on"))
                    matches = result.get("matches", [])
                    if result_domain in domains and len(matches) == 1:
                        peer_data = matches[0].get("company_data") or {}
                        basic_info = peer_data.get("basic_info") or {}
                        if _domain(basic_info.get("primary_domain")) == result_domain:
                            peer_profiles[result_domain] = peer_data
            except CrustdataServiceError as exc:
                context.extra_data["market_research"]["competitor_enrichment_error"] = str(exc)

        searches = []
        query_domains = domains or [None]
        for domain in query_domains:
            query = (
                f"{context.company_name} competitor {domain}"
                if domain
                else f"{context.company_name} {context.company_overview.sector if context.company_overview else ''} competitors"
            ).strip()
            try:
                results = await research_service.search_web(query, max_results=3)
            except CrustdataServiceError as exc:
                context.extra_data["market_research"]["web_search_error"] = str(exc)
                results = []
            searches.append((domain, results))

        page_urls = list(dict.fromkeys(
            result["url"] for _, results in searches for result in results if result.get("url")
        ))[:3]
        try:
            pages = await research_service.fetch_web_pages(page_urls)
        except CrustdataServiceError as exc:
            pages = []
            context.extra_data["market_research"]["web_enrichment_error"] = str(exc)
        pages_by_url = {page.get("url"): page for page in pages if isinstance(page, dict)}

        target_headcount = _number((company_data.get("headcount") or {}).get("total"))
        target_funding = _number((company_data.get("funding") or {}).get("total_investment_usd"))
        sources = []
        for domain, results in searches:
            for result in results:
                page = pages_by_url.get(result.get("url"), {})
                source = {
                    "title": result.get("title", "Web search result"),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "content": page.get("content", "") if isinstance(page.get("content"), str) else "",
                }
                sources.append(source)

            if not domain or domain not in peer_profiles:
                continue
            peer_data = peer_profiles[domain]
            basic_info = peer_data.get("basic_info") or {}
            peer_headcount = _number((peer_data.get("headcount") or {}).get("total"))
            peer_funding = _number((peer_data.get("funding") or {}).get("total_investment_usd"))
            size_pair = (
                (peer_headcount, target_headcount)
                if peer_headcount is not None and target_headcount is not None
                else (peer_funding, target_funding)
            )
            classification = _positioning(*size_pair)
            if classification is None:
                continue
            position, threat = classification
            relevant_source = next(
                (source for source in sources if _domain(source.get("url")) == domain),
                next((source for source in sources if source.get("url")), None),
            )
            evidence_text = (basic_info.get("description") or "").strip()
            if relevant_source:
                page_text = relevant_source.get("content") or relevant_source.get("snippet") or ""
                if page_text:
                    evidence_text = f"{evidence_text} Public source: {page_text[:500]}".strip()
                evidence_text = f"{evidence_text} Source: {relevant_source['url']}".strip()
            metric_name = "headcount" if size_pair[0] == peer_headcount else "total funding"
            evidence_text = (
                f"{evidence_text or 'Crustdata identified this domain as a competitor.'} "
                f"Positioning is inferred from relative {metric_name} versus the target, not market share."
            )
            context.competitors.append(
                Competitor(
                    name=basic_info.get("name") or domain,
                    description=evidence_text,
                    funding=_money(peer_funding),
                    positioning=position,
                    threat=threat,
                )
            )

        context.extra_data["market_research"]["sources"] = sources
        return context
