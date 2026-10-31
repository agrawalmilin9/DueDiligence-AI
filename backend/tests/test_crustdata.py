import asyncio
import json
from unittest.mock import AsyncMock

import httpx
import pytest

from app.pipeline.base import PipelineContext
from app.pipeline.stages.s1_company_identifier import CompanyIdentifierStage
from app.pipeline.stages.s2_company_info import CompanyInfoStage
from app.pipeline.stages.s6_risk_analyzer import RiskAnalyzerStage
from app.pipeline.stages.s5_claim_verifier import _verify_claim
from app.schemas.company import CompanyMetrics, CompanyOverview
from app.schemas.common import ClaimStatus
from app.services.crustdata import (
    API_VERSION,
    COMPANY_ENRICH_FIELDS,
    COMPANY_IDENTIFY_FIELDS,
    JOB_SEARCH_FIELDS,
    PERSON_SEARCH_FIELDS,
    CrustdataService,
    CrustdataServiceError,
    crustdata_service,
)
from app.services.research import ResearchService, research_service
from app.pipeline.stages.s5_claim_verifier import _extract_claims


class AsyncHandlerTransport(httpx.AsyncBaseTransport):
    def __init__(self, handler):
        self.handler = handler

    async def handle_async_request(self, request):
        return self.handler(request)


def _match(company_id=321, name="Example Company", domain="example.com", confidence=1.0, **extra):
    company_data = {
        "crustdata_company_id": company_id,
        "basic_info": {
            "name": name,
            "primary_domain": domain,
            "website": f"https://{domain}" if domain else None,
            "description": "A company description returned by Crustdata.",
            "year_founded": 2020,
            "industries": ["Software Development"],
        },
    }
    company_data.update(extra)
    return {"confidence_score": confidence, "company_data": company_data}


def _identify_response(*matches):
    return [{"matched_on": "Example Company", "match_type": "name", "matches": list(matches)}]


def _context(company_name="Example Company"):
    return PipelineContext(
        investigation_id="investigation-123",
        company_name=company_name,
        request="Review the company.",
    )


def _run(awaitable):
    return asyncio.run(awaitable)


def test_identify_company_uses_documented_post_request_and_headers():
    captured = {}
    response_data = _identify_response(_match())

    def handler(request):
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["headers"] = request.headers
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json=response_data)

    service = CrustdataService(
        api_key="test-api-key",
        base_url="https://api.crustdata.com",
        transport=AsyncHandlerTransport(handler),
    )
    result = _run(service.identify_company("Example Company"))

    assert result == response_data
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.crustdata.com/company/identify"
    assert captured["headers"]["Authorization"] == "Bearer test-api-key"
    assert API_VERSION == "2025-11-01"
    assert captured["headers"]["x-api-version"] == "2025-11-01"
    assert captured["json"] == {
        "names": ["Example Company"],
        "fields": COMPANY_IDENTIFY_FIELDS,
    }


def test_enrich_company_uses_documented_id_and_field_projection():
    captured = {}
    response_data = [{"matched_on": "321", "match_type": "crustdata_company_id", "matches": []}]

    def handler(request):
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["headers"] = request.headers
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json=response_data)

    service = CrustdataService(
        api_key="test-api-key",
        transport=AsyncHandlerTransport(handler),
    )
    result = _run(service.enrich_company(321))

    assert result == response_data
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.crustdata.com/company/enrich"
    assert captured["headers"]["x-api-version"] == "2025-11-01"
    assert captured["json"] == {
        "crustdata_company_ids": [321],
        "fields": COMPANY_ENRICH_FIELDS,
    }


@pytest.mark.parametrize(
    ("method_name", "path", "payload", "response"),
    [
        (
            "search_people",
            "/person/search",
            {
                "filters": {
                    "field": "experience.employment_details.current.company_id",
                    "type": "=",
                    "value": 321,
                },
                "fields": PERSON_SEARCH_FIELDS,
                "limit": 25,
            },
            {"profiles": [], "total_count": 0},
        ),
        (
            "search_jobs",
            "/job/search",
            {
                "filters": {
                    "field": "company.basic_info.company_id",
                    "type": "=",
                    "value": 321,
                },
                "fields": JOB_SEARCH_FIELDS,
                "limit": 20,
            },
            {"job_listings": [], "total_count": 0},
        ),
        (
            "search_web",
            "/web/search/live",
            {"query": "Example Company funding", "page": 1},
            {"success": True, "results": []},
        ),
        (
            "enrich_web_pages",
            "/web/enrich/live",
            {"urls": ["https://example.com/report"]},
            [{"success": True, "url": "https://example.com/report", "title": "Report", "content": ""}],
        ),
    ],
)
def test_research_endpoints_use_documented_paths_headers_and_payloads(
    method_name, path, payload, response
):
    captured = {}

    def handler(request):
        captured["request"] = request
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json=response)

    service = CrustdataService(
        api_key="test-api-key",
        transport=AsyncHandlerTransport(handler),
    )
    method = getattr(service, method_name)
    if method_name == "search_people":
        result = _run(method(321))
    elif method_name == "search_jobs":
        result = _run(method(321))
    elif method_name == "search_web":
        result = _run(method("Example Company funding"))
    else:
        result = _run(method(["https://example.com/report"]))

    request = captured["request"]
    assert request.method == "POST"
    assert request.url.path == path
    assert request.headers["Authorization"] == "Bearer test-api-key"
    assert request.headers["x-api-version"] == "2025-11-01"
    assert captured["json"] == payload
    assert result == response


def test_enrich_competitors_uses_domains_exact_match_and_profile_fields():
    captured = {}

    def handler(request):
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json=[])

    service = CrustdataService(
        api_key="test-api-key",
        transport=AsyncHandlerTransport(handler),
    )
    result = _run(service.enrich_competitors(["peer.example"]))

    assert result == []
    assert captured["json"] == {
        "domains": ["peer.example"],
        "fields": ["crustdata_company_id", "basic_info", "funding", "headcount"],
        "exact_match": True,
    }


def test_identify_stage_retains_company_id_and_matched_domain(monkeypatch):
    monkeypatch.setattr(
        crustdata_service,
        "identify_company",
        AsyncMock(return_value=_identify_response(_match(company_id=456, domain="actual.example"))),
    )
    context = _context()

    _run(CompanyIdentifierStage().execute(context))

    assert context.crustdata_company_id == 456
    assert context.matched_domain == "actual.example"
    assert context.company_overview.name == "Example Company"
    assert context.extra_data["company_identification_status"] == "identified"


def test_ambiguous_identification_does_not_select_or_enrich_a_candidate(monkeypatch):
    monkeypatch.setattr(
        crustdata_service,
        "identify_company",
        AsyncMock(
            return_value=_identify_response(
                _match(company_id=456, name="Example Company US", domain="example.com"),
                _match(company_id=789, name="Example Company UK", domain="example.co.uk", confidence=0.82),
            )
        ),
    )
    enrich = AsyncMock(return_value=[])
    monkeypatch.setattr(crustdata_service, "enrich_company", enrich)
    context = _context()

    _run(CompanyIdentifierStage().execute(context))
    _run(CompanyInfoStage().execute(context))

    assert context.crustdata_company_id is None
    assert context.matched_domain is None
    assert context.extra_data["company_identification_status"] == "ambiguous"
    assert "no candidate was selected or enriched" in context.company_overview.description
    assert "example.com" in context.company_overview.description
    enrich.assert_not_awaited()


def test_low_confidence_single_match_remains_unverified(monkeypatch):
    monkeypatch.setattr(
        crustdata_service,
        "identify_company",
        AsyncMock(return_value=_identify_response(_match(confidence=0.75))),
    )
    context = _context()

    _run(CompanyIdentifierStage().execute(context))

    assert context.crustdata_company_id is None
    assert context.extra_data["company_identification_status"] == "unverified"
    assert "confidence threshold" in context.company_overview.description


def test_razorpay_selects_exact_name_domain_candidate_over_related_companies(monkeypatch):
    response = _identify_response(
        _match(company_id=9101, name="Razorpay", domain="razorpay.com", confidence=1.0),
        _match(company_id=9102, name="Razorpay Software Private Limited", domain="razorpay.com", confidence=0.93),
        _match(company_id=9103, name="Razorpay Capital", domain="razorpay.com", confidence=0.88),
    )
    monkeypatch.setattr(crustdata_service, "identify_company", AsyncMock(return_value=response))
    context = _context(company_name="Razorpay")

    _run(CompanyIdentifierStage().execute(context))

    assert context.crustdata_company_id == 9101
    assert context.matched_domain == "razorpay.com"
    assert context.extra_data["company_identification_match_confidence"] == 1.0


def test_razorpay_domain_hint_selects_exact_domain_candidate(monkeypatch):
    response = _identify_response(
        _match(company_id=9101, name="Razorpay", domain="razorpay.in", confidence=0.9),
        _match(company_id=9102, name="Razorpay", domain="razorpay.com", confidence=0.98),
        _match(company_id=9103, name="Razorpay Technologies", domain="razorpay.com", confidence=0.9),
    )
    monkeypatch.setattr(crustdata_service, "identify_company", AsyncMock(return_value=response))
    context = _context(company_name="Razorpay (razorpay.com)")

    _run(CompanyIdentifierStage().execute(context))

    assert context.crustdata_company_id == 9102
    assert context.matched_domain == "razorpay.com"


def test_razorpay_identity_remains_unresolved_when_exact_candidate_does_not_lead(monkeypatch):
    response = _identify_response(
        _match(company_id=9101, name="Razorpay", domain="razorpay.com", confidence=0.95),
        _match(company_id=9102, name="Razorpay Software Private Limited", domain="razorpay.com", confidence=0.98),
    )
    monkeypatch.setattr(crustdata_service, "identify_company", AsyncMock(return_value=response))
    context = _context(company_name="Razorpay")

    _run(CompanyIdentifierStage().execute(context))

    assert context.crustdata_company_id is None
    assert context.extra_data["company_identification_status"] == "ambiguous"
    assert "clearly outrank alternatives" in context.company_overview.description


def test_company_info_enriches_by_crustdata_id_and_maps_returned_fields(monkeypatch):
    response = [
        {
            "matched_on": "456",
            "match_type": "crustdata_company_id",
            "matches": [
                {
                    "confidence_score": 1.0,
                    "company_data": {
                        "crustdata_company_id": 456,
                        "basic_info": {
                            "name": "Example Company",
                            "description": "Returned description.",
                            "website": "https://example.com",
                            "year_founded": 2020,
                        },
                        "funding": {
                            "total_investment_usd": 8000000,
                            "last_round_amount_usd": 3000000,
                            "last_round_type": "series_a",
                            "last_fundraise_date": "2025-02-01",
                            "investors": ["Example Ventures"],
                        },
                        "headcount": {
                            "total": 24,
                            "growth_percent": {"yoy": 22.2},
                        },
                        "locations": {"headquarters": "San Francisco, California, United States"},
                        "taxonomy": {"professional_network_industry": "Software Development"},
                    },
                }
            ],
        }
    ]
    enrich = AsyncMock(return_value=response)
    monkeypatch.setattr(crustdata_service, "enrich_company", enrich)
    context = _context()
    context.crustdata_company_id = 456
    context.matched_domain = "example.com"
    context.company_overview = CompanyOverview(
        name="Example Company",
        tagline="Not available from Crustdata",
        description="A company description returned by Crustdata.",
        sector="Software Development",
        stage="Not available from Crustdata",
        founded="2020",
        headquarters="Not available from Crustdata",
        website="https://example.com",
        business_model="Not available from Crustdata",
    )

    _run(CompanyInfoStage().execute(context))

    enrich.assert_awaited_once_with(456)
    assert context.metrics.total_funding == "$8,000,000"
    assert context.metrics.last_round == "Series A - $3,000,000"
    assert context.metrics.last_round_date == "2025-02-01"
    assert context.metrics.valuation == "Not available from Crustdata"
    assert context.metrics.employees == 24
    assert context.metrics.employee_growth == "+22.2% YoY"
    assert context.metrics.investors == ["Example Ventures"]
    assert context.company_overview.headquarters == "San Francisco, California, United States"


def test_razorpay_enrichment_maps_available_data_without_inventing_business_model(monkeypatch):
    response = [
        {
            "matched_on": "897127",
            "match_type": "crustdata_company_id",
            "matches": [
                {
                    "confidence_score": 1.0,
                    "company_data": {
                        "crustdata_company_id": 897127,
                        "basic_info": {
                            "name": "Razorpay",
                            "primary_domain": "razorpay.com",
                            "website": "https://bit.ly/razorpay_learnmore",
                            "year_founded": 2014,
                        },
                        "funding": {"total_investment_usd": 816600000, "investors": ["Example Capital"]},
                        "headcount": {"total": 4027},
                        "taxonomy": {"professional_network_industry": "Financial Services"},
                    },
                }
            ],
        }
    ]
    monkeypatch.setattr(crustdata_service, "enrich_company", AsyncMock(return_value=response))
    context = _context(company_name="Razorpay")
    context.crustdata_company_id = 897127
    context.matched_domain = "razorpay.com"
    context.company_overview = CompanyOverview(
        name="Razorpay",
        tagline="Not available from Crustdata",
        description="Not available from Crustdata",
        sector="Not available from Crustdata",
        stage="Not available from Crustdata",
        founded="2014",
        headquarters="Not available from Crustdata",
        website="https://bit.ly/razorpay_learnmore",
        business_model="Not available from Crustdata",
    )

    _run(CompanyInfoStage().execute(context))

    assert context.company_overview.website == "https://bit.ly/razorpay_learnmore"
    assert context.company_overview.sector == "Financial Services"
    assert context.company_overview.business_model == "Not available from Crustdata"
    assert context.metrics.total_funding == "$816,600,000"
    assert context.metrics.employees == 4027


def test_missing_employee_count_is_not_reported_as_zero(monkeypatch):
    response = [
        {
            "matched_on": "456",
            "match_type": "crustdata_company_id",
            "matches": [{"confidence_score": 1.0, "company_data": {"crustdata_company_id": 456}}],
        }
    ]
    monkeypatch.setattr(crustdata_service, "enrich_company", AsyncMock(return_value=response))
    context = _context()
    context.crustdata_company_id = 456

    _run(CompanyInfoStage().execute(context))

    assert context.metrics.employees == "Not available"


def test_missing_enrichment_fields_remain_unavailable(monkeypatch):
    monkeypatch.setattr(
        crustdata_service,
        "enrich_company",
        AsyncMock(
            return_value=[
                {
                    "matched_on": "456",
                    "match_type": "crustdata_company_id",
                    "matches": [
                        {"confidence_score": 1.0, "company_data": {"crustdata_company_id": 456}}
                    ],
                }
            ]
        ),
    )
    context = _context()
    context.crustdata_company_id = 456
    context.company_overview = CompanyOverview(
        name="Example Company",
        tagline="Not available from Crustdata",
        description="Not available from Crustdata",
        sector="Not available from Crustdata",
        stage="Not available from Crustdata",
        founded="Not available from Crustdata",
        headquarters="Not available from Crustdata",
        website="",
        business_model="Not available from Crustdata",
    )

    _run(CompanyInfoStage().execute(context))

    assert context.metrics.total_funding == "Not available from Crustdata"
    assert context.metrics.last_round == "Not available from Crustdata"
    assert context.metrics.valuation == "Not available from Crustdata"
    assert context.metrics.employees == "Not available"
    assert context.metrics.employee_growth == "Not available from Crustdata"
    assert context.metrics.investors == []


@pytest.mark.parametrize("status_code", [400, 401, 403, 429, 500])
def test_http_errors_are_clear_and_do_not_echo_response_body(status_code):
    def handler(request):
        return httpx.Response(status_code, json={"error": "secret-token-must-not-appear"})

    service = CrustdataService(
        api_key="test-api-key",
        transport=AsyncHandlerTransport(handler),
    )

    with pytest.raises(CrustdataServiceError) as error:
        _run(service.identify_company("Example Company"))

    assert f"HTTP {status_code}" in str(error.value)
    assert "secret-token-must-not-appear" not in str(error.value)
    assert "test-api-key" not in str(error.value)


def test_timeout_has_a_sanitized_error():
    def handler(request):
        raise httpx.ReadTimeout("secret-token-must-not-appear", request=request)

    service = CrustdataService(
        api_key="test-api-key",
        transport=AsyncHandlerTransport(handler),
    )

    with pytest.raises(CrustdataServiceError, match="company identification timed out"):
        _run(service.identify_company("Example Company"))


@pytest.mark.parametrize(
    ("claim", "pages", "expected"),
    [
        (
            "Example Company raised $10 million funding.",
            [
                {"success": True, "url": "https://news-one.example/report", "title": "Report", "content": "Example Company raised $10 million funding."},
                {"success": True, "url": "https://news-two.example/filing", "title": "Filing", "content": "Example Company raised $10 million funding."},
            ],
            ClaimStatus.VERIFIED,
        ),
        (
            "Example Company has no debt.",
            [
                {"success": True, "url": "https://news-one.example/report", "title": "Report", "content": "Example Company has debt."},
                {"success": True, "url": "https://news-two.example/filing", "title": "Filing", "content": "Example Company has debt."},
            ],
            ClaimStatus.CONTRADICTED,
        ),
        (
            "Example Company has no debt.",
            [
                {"success": True, "url": "https://news-one.example/report", "title": "Report", "content": "Example Company has no debt."},
                {"success": True, "url": "https://news-two.example/filing", "title": "Filing", "content": "Example Company has debt."},
            ],
            ClaimStatus.CONFLICTING,
        ),
        (
            "Example Company raised $10 million funding.",
            [{"success": True, "url": "https://news-one.example/report", "title": "Report", "content": "Example Company announced a product update."}],
            ClaimStatus.UNVERIFIED,
        ),
    ],
)
def test_claim_verification_requires_matching_evidence_from_independent_hosts(claim, pages, expected):
    status, evidence, source = _verify_claim(claim, pages)

    assert status == expected
    assert source.url == pages[0]["url"]
    assert evidence


def test_razorpay_numbered_claims_section_is_extracted():
    request = """Company: Razorpay
Request: Assess the company for a potential investment.

Claims:
1. Razorpay provides payment processing to businesses.
2. Razorpay was founded in 2014.
"""

    assert _extract_claims(request) == [
        "Razorpay provides payment processing to businesses.",
        "Razorpay was founded in 2014.",
    ]


@pytest.mark.parametrize("item_prefix", ["- ", "* ", "1) ", "1. "])
def test_claims_section_supports_bullets_and_numbering(item_prefix):
    request = f"Claims:\n{item_prefix}Razorpay provides payment processing.\n"

    assert _extract_claims(request) == ["Razorpay provides payment processing."]


def test_claims_section_supports_unicode_bullet_input():
    request = f"Claims:\n{chr(8226)} Razorpay provides payment processing.\n"

    assert _extract_claims(request) == ["Razorpay provides payment processing."]


def test_individual_claim_lines_are_extracted():
    request = "Claim: Razorpay provides payment processing.\nClaim: Razorpay was founded in 2014."

    assert _extract_claims(request) == [
        "Razorpay provides payment processing.",
        "Razorpay was founded in 2014.",
    ]


def test_web_search_parser_preserves_documented_titles_urls_and_snippets(monkeypatch):
    response = {
        "success": True,
        "query": "Razorpay business model",
        "results": [
            {
                "title": "Razorpay Company Profile",
                "url": "https://razorpay.com/about/",
                "snippet": "Payment and financial solutions for businesses.",
            }
        ],
    }
    monkeypatch.setattr(crustdata_service, "search_web", AsyncMock(return_value=response))

    results = _run(ResearchService().search_web("Razorpay business model"))

    assert results == [
        {
            "title": "Razorpay Company Profile",
            "url": "https://razorpay.com/about/",
            "snippet": "Payment and financial solutions for businesses.",
        }
    ]


def test_web_search_parser_ignores_unsuccessful_response(monkeypatch):
    monkeypatch.setattr(
        crustdata_service,
        "search_web",
        AsyncMock(return_value={"success": False, "results": [{"title": "Stale", "url": "https://example.com"}]}),
    )

    assert _run(ResearchService().search_web("Razorpay")) == []


def test_empty_founder_hiring_and_competitor_results_are_not_reported_as_absence():
    context = _context("Razorpay")
    context.crustdata_company_id = 897127
    context.matched_domain = "razorpay.com"
    context.metrics = CompanyMetrics(
        total_funding="Not available from Crustdata",
        last_round="Not available from Crustdata",
        last_round_date="Not available from Crustdata",
        valuation="Not available from Crustdata",
        employees="Not available",
        employee_growth="Not available from Crustdata",
        investors=[],
    )
    context.extra_data["founder_research_status"] = "completed"
    context.extra_data["hiring_research"] = {"jobs": []}
    context.extra_data["market_research"] = {"sources": []}

    _run(RiskAnalyzerStage().execute(context))

    descriptions = " ".join(risk.description for risk in context.risks)
    assert "does not establish that the company has no founders" in descriptions
    assert "does not establish that the company is not hiring" in descriptions
    assert "not evidence that competitors are absent" in descriptions