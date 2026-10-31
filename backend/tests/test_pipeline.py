import asyncio
from unittest.mock import AsyncMock

from app.pipeline.orchestrator import PipelineOrchestrator
from app.schemas.common import ClaimStatus, Recommendation
from app.services.crustdata import crustdata_service


def test_pipeline_orchestrator_7_stages():
    orchestrator = PipelineOrchestrator()
    assert len(orchestrator.stages) == 7

    stage_ids = [s.stage_id for s in orchestrator.stages]
    assert stage_ids == [
        "identify",
        "company_info",
        "founders",
        "market",
        "claims",
        "risks",
        "report",
    ]

    report = asyncio.run(
        orchestrator.run(
            investigation_id="test-entity-run",
            company_name="Test Robotics Entity",
            request="Seed investment evaluation of $1M.",
        )
    )

    # Verify report is compiled and valid
    assert report.id == "test-entity-run"
    assert report.company.name == "Test Robotics Entity"
    assert report.recommendation.verdict == Recommendation.PROCEED_WITH_CAUTION

    # Company profile and metrics come from the mocked Crustdata responses.
    assert report.company.description == "Verified profile description."
    assert report.company.website == "https://example.test"
    assert report.metrics.total_funding == "$10,000,000"
    assert report.metrics.employees == 12
    assert len(report.founders) == 1
    assert report.founders[0].name == "Avery Founder"
    assert report.founders[0].role.startswith("Inferred founder:")
    assert "not independent verification" in report.founders[0].background
    assert len(report.competitors) == 2
    assert {competitor.positioning for competitor in report.competitors} == {"Challenger"}
    assert len(report.claims) == 0
    assert any("Indexed hiring activity" == finding.title for finding in report.findings)
    assert report.recommendation.verdict == Recommendation.PROCEED_WITH_CAUTION
    assert "No claims were invented" in report.memo.sections[4].body


def test_pipeline_verifies_only_explicit_claims_with_source_urls():
    report = asyncio.run(
        PipelineOrchestrator().run(
            investigation_id="test-claims-run",
            company_name="Test Robotics Entity",
            request="Evaluate the company.\nClaims: Test Robotics Entity reports $10 million funding.",
        )
    )

    assert len(report.claims) == 1
    claim = report.claims[0]
    assert claim.status == ClaimStatus.VERIFIED
    assert claim.source.url.startswith("https://")
    assert "Matching source hosts: 2" in claim.evidence
    assert "[Scaffold]" not in claim.evidence
    assert any("Software Engineer - https://jobs.example/role/1" in section.body for section in report.memo.sections)


def test_razorpay_numbered_claims_complete_pipeline_with_sources(monkeypatch):
    identify = AsyncMock(
        return_value=[
            {
                "matched_on": "Razorpay",
                "match_type": "name",
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
                                "industries": ["Financial Services"],
                            },
                        },
                    },
                    {
                        "confidence_score": 0.8,
                        "company_data": {
                            "crustdata_company_id": 1216740,
                            "basic_info": {
                                "name": "Razorpay Curlec",
                                "primary_domain": "razorpay.com",
                                "website": "http://www.curlec.com",
                            },
                        },
                    },
                    {
                        "confidence_score": 0.8,
                        "company_data": {
                            "crustdata_company_id": 17011741,
                            "basic_info": {
                                "name": "Razorpay US",
                                "primary_domain": "razorpay.com",
                                "website": "https://razorpay.com/us/",
                            },
                        },
                    },
                ],
            }
        ]
    )
    enrich = AsyncMock(
        return_value=[
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
                            "funding": {"total_investment_usd": 816600000},
                            "headcount": {"total": 4027},
                            "taxonomy": {"professional_network_industry": "Financial Services"},
                        },
                    }
                ],
            }
        ]
    )
    monkeypatch.setattr(crustdata_service, "identify_company", identify)
    monkeypatch.setattr(crustdata_service, "enrich_company", enrich)
    request = (
        "Review Razorpay for a potential investment.\n\n"
        "Claims:\n"
        "1. Razorpay provides payment processing to businesses.\n"
        "2. Razorpay was founded in 2014."
    )

    report = asyncio.run(
        PipelineOrchestrator().run(
            investigation_id="razorpay-regression",
            company_name="Razorpay",
            request=request,
        )
    )

    identify.assert_awaited_once_with("Razorpay")
    enrich.assert_awaited_once_with(897127)
    assert report.company.name == "Razorpay"
    assert report.company.sector == "Financial Services"
    assert report.company.website == "https://bit.ly/razorpay_learnmore"
    assert report.metrics.total_funding == "$816,600,000"
    assert report.metrics.employees == 4027
    assert len(report.claims) == 2
    assert all(claim.source.url.startswith("https://") for claim in report.claims)
    assert "news.example" in report.memo.sections[-1].body
    assert "press.example" in report.memo.sections[-1].body
