"""HTTP client for the documented Crustdata company endpoints."""

from typing import Any, Dict, List, Optional

import httpx

from ..config import settings


API_VERSION = "2025-11-01"
COMPANY_IDENTIFY_FIELDS = ["crustdata_company_id", "basic_info"]
COMPANY_ENRICH_FIELDS = [
    "crustdata_company_id",
    "basic_info",
    "funding",
    "headcount",
    "locations",
    "taxonomy",
    "competitors.all_domains",
    "hiring.openings_count",
    "hiring.openings_growth_percent",
    "hiring.recent_titles_csv",
    "market_intel",
]
COMPETITOR_ENRICH_FIELDS = ["crustdata_company_id", "basic_info", "funding", "headcount"]
PERSON_SEARCH_FIELDS = [
    "crustdata_person_id",
    "basic_profile.name",
    "basic_profile.current_title",
    "basic_profile.headline",
    "experience.employment_details.current",
    "experience.employment_details.past",
    "social_handles.professional_network_identifier.profile_url",
]
JOB_SEARCH_FIELDS = ["crustdata_job_id", "job_details", "company", "location", "metadata"]


class CrustdataServiceError(RuntimeError):
    """A sanitized error returned by the Crustdata integration."""


def flatten_company_matches(response: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for result in response:
        for match in result["matches"]:
            matches.append(
                {
                    "matched_on": result.get("matched_on"),
                    "match_type": result.get("match_type"),
                    "confidence_score": match.get("confidence_score"),
                    "company_data": match.get("company_data"),
                }
            )
    return matches


class CrustdataService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 15.0,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ):
        self.api_key = settings.CRUSTDATA_API_KEY if api_key is None else api_key
        self.base_url = (base_url or settings.CRUSTDATA_BASE_URL).rstrip("/")
        self.timeout = httpx.Timeout(timeout, connect=min(timeout, 5.0))
        self.transport = transport
        self.is_configured = bool(self.api_key.strip())

    async def identify_company(self, company_name: str) -> List[Dict[str, Any]]:
        return await self._post(
            "/company/identify",
            {
                "names": [company_name],
                "fields": COMPANY_IDENTIFY_FIELDS,
            },
        )

    async def enrich_company(self, company_id: int) -> List[Dict[str, Any]]:
        return await self._post(
            "/company/enrich",
            {
                "crustdata_company_ids": [company_id],
                "fields": COMPANY_ENRICH_FIELDS,
            },
        )

    async def enrich_competitors(self, domains: List[str]) -> List[Dict[str, Any]]:
        if not domains:
            return []
        return await self._post(
            "/company/enrich",
            {
                "domains": domains[:25],
                "fields": COMPETITOR_ENRICH_FIELDS,
                "exact_match": True,
            },
        )

    async def search_people(self, company_id: int, limit: int = 25) -> Dict[str, Any]:
        data = await self._post_json(
            "/person/search",
            {
                "filters": {
                    "field": "experience.employment_details.current.company_id",
                    "type": "=",
                    "value": company_id,
                },
                "fields": PERSON_SEARCH_FIELDS,
                "limit": limit,
            },
            "people search",
        )
        if not isinstance(data, dict) or not isinstance(data.get("profiles"), list):
            raise CrustdataServiceError("Crustdata people search returned an unexpected response structure.")
        return data

    async def search_jobs(self, company_id: int, limit: int = 20) -> Dict[str, Any]:
        data = await self._post_json(
            "/job/search",
            {
                "filters": {
                    "field": "company.basic_info.company_id",
                    "type": "=",
                    "value": company_id,
                },
                "fields": JOB_SEARCH_FIELDS,
                "limit": limit,
            },
            "job search",
        )
        if not isinstance(data, dict) or not isinstance(data.get("job_listings"), list):
            raise CrustdataServiceError("Crustdata job search returned an unexpected response structure.")
        return data

    async def search_web(self, query: str, page: int = 1) -> Dict[str, Any]:
        data = await self._post_json(
            "/web/search/live",
            {"query": query, "page": page},
            "web search",
        )
        if not isinstance(data, dict) or not isinstance(data.get("results"), list):
            raise CrustdataServiceError("Crustdata web search returned an unexpected response structure.")
        return data

    async def enrich_web_pages(self, urls: List[str]) -> List[Dict[str, Any]]:
        if not urls:
            return []
        data = await self._post_json(
            "/web/enrich/live",
            {"urls": urls[:10]},
            "web page enrichment",
        )
        if not isinstance(data, list) or any(not isinstance(page, dict) for page in data):
            raise CrustdataServiceError("Crustdata web enrichment returned an unexpected response structure.")
        return data

    async def _post(self, path: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = await self._post_json(
            path,
            payload,
            "company identification" if path.endswith("identify") else "company enrichment",
        )
        if not isinstance(data, list) or any(
            not isinstance(result, dict) or not isinstance(result.get("matches"), list)
            for result in data
        ):
            raise CrustdataServiceError("Crustdata company operation returned an unexpected response structure.")
        return data

    async def _post_json(
        self,
        path: str,
        payload: Dict[str, Any],
        operation: str,
    ) -> Any:
        if not self.is_configured:
            raise CrustdataServiceError("Crustdata API key is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "x-api-version": API_VERSION,
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                transport=self.transport,
            ) as client:
                response = await client.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers=headers,
                )
        except httpx.TimeoutException as exc:
            raise CrustdataServiceError(f"Crustdata {operation} timed out.") from exc
        except httpx.RequestError as exc:
            raise CrustdataServiceError(
                f"Could not reach Crustdata for {operation}."
            ) from exc

        if response.status_code == 404:
            return []
        if response.is_error:
            reason = {
                400: "the request was rejected as invalid",
                401: "authentication failed",
                403: "permission or credit access was denied",
                429: "the rate limit was exceeded",
            }.get(response.status_code, "the upstream request failed")
            raise CrustdataServiceError(
                f"Crustdata {operation} failed (HTTP {response.status_code}: {reason})."
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise CrustdataServiceError(
                f"Crustdata {operation} returned invalid JSON."
            ) from exc

        return data


crustdata_service = CrustdataService()
