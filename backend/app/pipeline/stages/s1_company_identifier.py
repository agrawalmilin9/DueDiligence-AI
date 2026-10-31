"""
Stage 1: Company Identification
--------------------------------
Resolves legal entity, domain, and registry records.
Modular scaffold awaiting Crustdata / registry search integration.
"""

import re
from urllib.parse import urlparse

from ..base import BasePipelineStage, PipelineContext
from ...schemas.company import CompanyOverview
from ...services.crustdata import crustdata_service, flatten_company_matches


UNAVAILABLE = "Not available from Crustdata"
MIN_MATCH_CONFIDENCE = 0.9
MIN_CONFIDENCE_LEAD = 0.05
DOMAIN_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+", re.IGNORECASE)


def _text(value):
    if isinstance(value, (str, int, float)) and not isinstance(value, bool):
        value = str(value).strip()
        return value or None
    return None


def _first_industry(value):
    if isinstance(value, list):
        return next((industry for industry in value if isinstance(industry, str) and industry.strip()), None)
    return _text(value)


def _normalize_name(value):
    if not isinstance(value, str):
        return ""
    value = DOMAIN_PATTERN.sub(" ", value)
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _normalize_domain(value):
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = urlparse(value.strip() if "://" in value else f"https://{value.strip()}")
    host = (parsed.hostname or "").lower().removeprefix("www.").rstrip(".")
    return host or None


def _requested_domain(company_name, request):
    input_domains = DOMAIN_PATTERN.findall(company_name)
    if input_domains:
        return _normalize_domain(input_domains[0])
    domain_hint = re.search(
        r"\b(?:company\s+)?(?:domain|website)\s*[:=]\s*((?:https?://)?(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+)",
        request,
        re.IGNORECASE,
    )
    return _normalize_domain(domain_hint.group(1)) if domain_hint else None


def _select_company_match(matches, company_name, request):
    normalized_name = _normalize_name(company_name)
    exact_name_matches = [
        match
        for match in matches
        if _normalize_name(((match.get("company_data") or {}).get("basic_info") or {}).get("name"))
        == normalized_name
    ]
    if not exact_name_matches:
        return None, "no exact company-name match"

    domain = _requested_domain(company_name, request)
    if domain is None:
        exact_name_domains = {
            _normalize_domain(
                (((match.get("company_data") or {}).get("basic_info") or {}).get("primary_domain"))
            )
            for match in exact_name_matches
        }
        exact_name_domains.discard(None)
        if len(exact_name_domains) != 1:
            return None, "exact company name maps to multiple or missing domains"
        domain = next(iter(exact_name_domains))

    exact_matches = [
        match
        for match in exact_name_matches
        if _normalize_domain(
            (((match.get("company_data") or {}).get("basic_info") or {}).get("primary_domain"))
        ) == domain
    ]
    if len(exact_matches) != 1:
        return None, "exact company name and domain did not identify one candidate"

    selected = exact_matches[0]
    company_data = selected.get("company_data") or {}
    company_id = company_data.get("crustdata_company_id")
    confidence = selected.get("confidence_score")
    if (
        isinstance(company_id, bool)
        or not isinstance(company_id, int)
        or isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or confidence < MIN_MATCH_CONFIDENCE
        or confidence > 1
    ):
        return None, "exact company candidate did not meet the confidence threshold"

    alternative_scores = [
        match.get("confidence_score")
        for match in matches
        if match is not selected
        and isinstance(match.get("confidence_score"), (int, float))
        and not isinstance(match.get("confidence_score"), bool)
    ]
    if alternative_scores and confidence - max(alternative_scores) < MIN_CONFIDENCE_LEAD:
        return None, "exact company candidate did not clearly outrank alternatives"

    return selected, "exact name, exact domain, and confidence matched"


def _candidate_description(matches, status):
    if not matches:
        return "Crustdata returned no company match. Company identity is unverified."

    candidates = []
    for match in matches:
        company_data = match.get("company_data") or {}
        basic_info = company_data.get("basic_info") or {}
        name = _text(basic_info.get("name")) or "Unknown company"
        domain = _text(basic_info.get("primary_domain")) or "domain unavailable"
        confidence = match.get("confidence_score")
        score = f", confidence {confidence:.2f}" if isinstance(confidence, (int, float)) else ""
        candidates.append(f"{name} ({domain}{score})")
    return (
        f"Company identity is unverified ({status}); no candidate was selected or enriched. "
        f"Crustdata candidates: {', '.join(candidates)}."
    )


def _unverified_overview(company_name, matches, status):
    return CompanyOverview(
        name=company_name,
        tagline="Unverified company identity",
        description=_candidate_description(matches, status),
        sector=UNAVAILABLE,
        stage=UNAVAILABLE,
        founded=UNAVAILABLE,
        headquarters=UNAVAILABLE,
        website="",
        business_model=UNAVAILABLE,
    )


class CompanyIdentifierStage(BasePipelineStage):
    @property
    def stage_id(self) -> str:
        return "identify"

    @property
    def stage_name(self) -> str:
        return "Identifying company"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        response = await crustdata_service.identify_company(context.company_name)
        matches = flatten_company_matches(response)
        context.extra_data["crustdata_identify_response"] = response

        selected, selection_reason = _select_company_match(matches, context.company_name, context.request)
        if selected is None:
            status = "no match" if not matches else selection_reason
            identity_status = (
                "not_found"
                if not matches
                else "unverified"
                if selection_reason == "exact company candidate did not meet the confidence threshold"
                or (selection_reason == "no exact company-name match" and len(matches) == 1)
                else "ambiguous"
            )
            context.extra_data["company_identification_status"] = identity_status
            context.extra_data["company_match_candidates"] = matches
            context.company_overview = _unverified_overview(context.company_name, matches, status)
            return context

        match = selected
        company_data = match.get("company_data") or {}
        basic_info = company_data.get("basic_info") or {}
        company_id = company_data.get("crustdata_company_id")
        confidence = match.get("confidence_score")
        context.crustdata_company_id = company_id
        context.matched_domain = _text(basic_info.get("primary_domain"))
        context.extra_data["company_identification_status"] = "identified"
        context.extra_data["company_identification_match_confidence"] = confidence
        context.extra_data["company_identification_selection_reason"] = selection_reason
        context.extra_data["crustdata_company_id"] = company_id
        context.extra_data["matched_domain"] = context.matched_domain

        context.company_overview = CompanyOverview(
            name=_text(basic_info.get("name")) or context.company_name,
            tagline="Not available from Crustdata",
            description=_text(basic_info.get("description")) or UNAVAILABLE,
            sector=_first_industry(basic_info.get("industries")) or UNAVAILABLE,
            stage=UNAVAILABLE,
            founded=_text(basic_info.get("year_founded")) or UNAVAILABLE,
            headquarters=UNAVAILABLE,
            website=_text(basic_info.get("website")) or "",
            business_model=UNAVAILABLE,
        )
        return context
