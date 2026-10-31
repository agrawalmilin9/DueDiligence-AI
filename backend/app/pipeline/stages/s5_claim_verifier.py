"""Stage 5: evaluate explicitly supplied claims against fetched public pages."""

import html
import re
from urllib.parse import urlparse

from ..base import BasePipelineStage, PipelineContext
from ...schemas.common import ClaimStatus, Source
from ...schemas.report import Claim
from ...services.crustdata import CrustdataServiceError
from ...services.research import research_service


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "of", "on", "or", "that", "the", "their", "this", "to", "was",
    "were", "will", "with",
}
NEGATION_WORDS = {"no", "not", "never", "false", "denied", "disputed", "incorrect", "without"}
CLAIMS_HEADER = re.compile(r"^\s*claims?(?:\s+to\s+verify)?\s*:\s*(.*?)\s*$", re.IGNORECASE)
SINGLE_CLAIM = re.compile(r"^\s*claim(?:\s+\d+)?\s*:\s*(.+?)\s*$", re.IGNORECASE)
LIST_ITEM = re.compile(r"^\s*(?:[-*\u2022]\s+|\d+\s*[.)]\s*)(.+?)\s*$")


def _append_claims(claims, value):
    for statement in re.split(r"\s*;\s*", value):
        statement = statement.strip().strip('"\u201c\u201d\' ')
        if statement:
            claims.append(statement)


def _extract_claims(request):
    claims = []
    in_claims_section = False
    for line in request.splitlines():
        single_claim = SINGLE_CLAIM.match(line)
        if single_claim:
            _append_claims(claims, single_claim.group(1))
            in_claims_section = False
            continue
        heading = CLAIMS_HEADER.match(line)
        if heading:
            in_claims_section = True
            if heading.group(1):
                _append_claims(claims, heading.group(1))
            continue
        if not in_claims_section:
            continue
        if not line.strip():
            continue
        list_item = LIST_ITEM.match(line)
        if list_item:
            _append_claims(claims, list_item.group(1))
        else:
            in_claims_section = False
    return list(dict.fromkeys(claims))[:3]


def _page_text(page):
    content = page.get("content") or ""
    if not isinstance(content, str):
        return ""
    content = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", content, flags=re.IGNORECASE | re.DOTALL)
    content = html.unescape(re.sub(r"<[^>]+>", " ", content))
    return re.sub(r"\s+", " ", content).strip()


def _claim_polarity(claim, text):
    terms = {
        token
        for token in re.findall(r"[a-z0-9]+", claim.lower())
        if len(token) > 2 and token not in STOP_WORDS and token not in NEGATION_WORDS
    }
    if not terms:
        return None
    claim_is_negative = bool(set(re.findall(r"[a-z0-9]+", claim.lower())) & NEGATION_WORDS)
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        sentence_words = set(re.findall(r"[a-z0-9]+", sentence.lower()))
        if len(terms & sentence_words) / len(terms) < 0.8:
            continue
        sentence_is_negative = bool(sentence_words & NEGATION_WORDS)
        return "negative" if sentence_is_negative != claim_is_negative else "positive"
    return None


def _verify_claim(claim, pages):
    positive_hosts = set()
    negative_hosts = set()
    evidence = []
    relevant_pages = []
    for page in pages:
        if not page.get("success"):
            continue
        text = _page_text(page)
        polarity = _claim_polarity(claim, text)
        if polarity is None:
            continue
        host = (urlparse(page.get("url", "")).hostname or "").lower().removeprefix("www.")
        if not host:
            continue
        relevant_pages.append(page)
        (positive_hosts if polarity == "positive" else negative_hosts).add(host)
        evidence.append(f"{page.get('title') or host}: {text[:300]}")

    if positive_hosts and negative_hosts:
        status = ClaimStatus.CONFLICTING
    elif len(positive_hosts) >= 2:
        status = ClaimStatus.VERIFIED
    elif len(negative_hosts) >= 2:
        status = ClaimStatus.CONTRADICTED
    else:
        status = ClaimStatus.UNVERIFIED

    source_page = relevant_pages[0] if relevant_pages else next(
        (page for page in pages if page.get("success") and page.get("url")),
        None,
    )
    source = Source(
        title=source_page.get("title") or "No matching source page",
        url=source_page.get("url") or "",
    ) if source_page else Source(title="No source found", url="")
    detail = "; ".join(evidence) if evidence else "Fetched pages did not contain enough matching text to assess this claim."
    detail += f" Matching source hosts: {len(positive_hosts)}; contradicting source hosts: {len(negative_hosts)}."
    return status, detail, source


class ClaimVerifierStage(BasePipelineStage):
    @property
    def stage_id(self) -> str:
        return "claims"

    @property
    def stage_name(self) -> str:
        return "Verifying claims"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        context.claims = []
        claims = _extract_claims(context.request)
        context.extra_data["claim_verification_status"] = "completed" if claims else "no_explicit_claims"
        if claims and context.crustdata_company_id is None:
            context.extra_data["claim_verification_status"] = "company_identity_unverified"
            context.claims = [
                Claim(
                    id=f"claim-{index}",
                    claim=statement,
                    status=ClaimStatus.UNVERIFIED,
                    evidence="Company identity is unresolved; public pages cannot safely be attributed to this target.",
                    source=Source(title="Company identity unverified", url=""),
                )
                for index, statement in enumerate(claims, start=1)
            ]
            return context

        for index, statement in enumerate(claims, start=1):
            query = f"{context.company_name} {context.matched_domain or ''} {statement}".strip()
            try:
                search_results = await research_service.search_web(query, max_results=3)
                urls = list(dict.fromkeys(result["url"] for result in search_results if result.get("url")))[:2]
                pages = await research_service.fetch_web_pages(urls)
            except CrustdataServiceError as exc:
                pages = []
                context.extra_data.setdefault("claim_verification_errors", []).append(str(exc))

            status, evidence, source = _verify_claim(statement, pages)
            context.claims.append(
                Claim(
                    id=f"claim-{index}",
                    claim=statement,
                    status=status,
                    evidence=evidence,
                    source=source,
                )
            )
        return context
