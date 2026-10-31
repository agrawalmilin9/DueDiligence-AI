import pytest
from starlette.testclient import TestClient
from app.main import app
from app.services.crustdata import crustdata_service
from app.services.research import research_service


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def mock_crustdata_pipeline_calls(monkeypatch):
    matched_names = {}
    last_web_query = {"query": ""}

    async def identify_company(company_name):
        matched_names[987654] = company_name
        return [
            {
                "matched_on": company_name,
                "match_type": "name",
                "matches": [
                    {
                        "confidence_score": 1.0,
                        "company_data": {
                            "crustdata_company_id": 987654,
                            "basic_info": {
                                "name": company_name,
                                "primary_domain": "example.test",
                                "website": "https://example.test",
                                "description": f"Verified profile for {company_name}.",
                                "year_founded": 2022,
                                "industries": ["Software Development"],
                            },
                        },
                    }
                ],
            }
        ]

    async def enrich_company(company_id):
        return [
            {
                "matched_on": str(company_id),
                "match_type": "crustdata_company_id",
                "matches": [
                    {
                        "confidence_score": 1.0,
                        "company_data": {
                            "crustdata_company_id": company_id,
                            "basic_info": {
                                "name": matched_names.get(company_id, "Pipeline Test Company"),
                                "description": "Verified profile description.",
                                "website": "https://example.test",
                            },
                            "funding": {
                                "total_investment_usd": 10000000,
                                "last_round_amount_usd": 3000000,
                                "last_round_type": "series_a",
                                "last_fundraise_date": "2025-02-01",
                                "investors": ["Example Ventures"],
                            },
                            "headcount": {
                                "total": 12,
                                "growth_percent": {"yoy": 10.0},
                            },
                            "locations": {"headquarters": "San Francisco, California, United States"},
                            "taxonomy": {"professional_network_industry": "Software Development"},
                            "competitors": {"all_domains": ["peer.example", "niche.example"]},
                            "hiring": {
                                "openings_count": 2,
                                "openings_growth_percent": {"yoy": 15.0},
                                "recent_titles_csv": "Software Engineer, Product Manager",
                            },
                        },
                    }
                ],
            }
        ]

    async def search_people(company_id, limit=25):
        return {
            "profiles": [
                {
                    "basic_profile": {"name": "Avery Founder", "current_title": "Co-Founder and CEO"},
                    "social_handles": {
                        "professional_network_identifier": {
                            "profile_url": "https://www.linkedin.com/in/avery-founder",
                        }
                    },
                    "experience": {
                        "employment_details": {
                            "current": [{"title": "Co-Founder and CEO", "crustdata_company_id": company_id}],
                            "past": [{"name": "Prior Company", "crustdata_company_id": 123}],
                        }
                    },
                },
                {
                    "basic_profile": {"name": "Casey Employee", "current_title": "Engineer"},
                    "experience": {"employment_details": {"current": [{"title": "Engineer"}], "past": []}},
                },
            ],
            "total_count": 2,
        }

    async def search_jobs(company_id, limit=20):
        return {
            "job_listings": [
                {
                    "job_details": {
                        "title": "Software Engineer",
                        "url": "https://jobs.example/role/1",
                        "workplace_type": "Hybrid",
                    },
                    "location": {"raw": "San Francisco, California"},
                    "metadata": {"date_added": "2026-10-01"},
                },
                {
                    "job_details": {
                        "title": "Product Manager",
                        "url": "https://jobs.example/role/2",
                        "workplace_type": "Remote",
                    },
                    "location": {"raw": "United States"},
                    "metadata": {"date_added": "2026-10-02"},
                },
            ],
            "total_count": 2,
        }

    async def enrich_competitors(domains):
        profiles = {
            "peer.example": ("Peer Systems", 60, 20000000),
            "niche.example": ("Niche Tools", 3, 1000000),
        }
        return [
            {
                "matched_on": domain,
                "match_type": "domain",
                "matches": [
                    {
                        "confidence_score": 1.0,
                        "company_data": {
                            "crustdata_company_id": index,
                            "basic_info": {
                                "name": profiles[domain][0],
                                "primary_domain": domain,
                                "description": f"Verified profile for {profiles[domain][0]}.",
                            },
                            "headcount": {"total": profiles[domain][1]},
                            "funding": {"total_investment_usd": profiles[domain][2]},
                        },
                    }
                ],
            }
            for index, domain in enumerate(domains, start=1)
            if domain in profiles
        ]

    async def search_web(query, max_results=5):
        last_web_query["query"] = query
        return [
            {"title": "Company report", "url": "https://news.example/company-report", "snippet": query},
            {"title": "Independent filing coverage", "url": "https://press.example/filing-coverage", "snippet": query},
        ][:max_results]

    async def fetch_web_pages(urls):
        query = last_web_query["query"]
        return [
            {
                "success": True,
                "url": url,
                "title": url.rsplit("/", 1)[-1],
                "content": f"<html><body>{query}. Independent reporting details.</body></html>",
            }
            for url in urls
        ]

    monkeypatch.setattr(crustdata_service, "identify_company", identify_company)
    monkeypatch.setattr(crustdata_service, "enrich_company", enrich_company)
    monkeypatch.setattr(crustdata_service, "search_people", search_people)
    monkeypatch.setattr(crustdata_service, "search_jobs", search_jobs)
    monkeypatch.setattr(crustdata_service, "enrich_competitors", enrich_competitors)
    monkeypatch.setattr(research_service, "search_web", search_web)
    monkeypatch.setattr(research_service, "fetch_web_pages", fetch_web_pages)
