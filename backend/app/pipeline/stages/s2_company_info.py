"""
Stage 2: Company Information Retrieval
--------------------------------------
Retrieves verified financial rounds, valuation estimates, and employee metrics.
Modular scaffold awaiting Crustdata / SEC / Crunchbase integration.
"""

from ..base import BasePipelineStage, PipelineContext
from ...schemas.company import CompanyMetrics
from ...services.crustdata import crustdata_service, flatten_company_matches


UNAVAILABLE = "Not available from Crustdata"


def _text(value):
    if isinstance(value, (str, int, float)) and not isinstance(value, bool):
        value = str(value).strip()
        return value or None
    return None


def _currency(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return UNAVAILABLE
    if float(value).is_integer():
        return f"${value:,.0f}"
    return f"${value:,.2f}"


def _round_name(value):
    text = _text(value)
    return text.replace("_", " ").title() if text else None


def _industry(taxonomy, basic_info):
    primary = _text(taxonomy.get("professional_network_industry"))
    if primary:
        return primary
    industries = taxonomy.get("professional_network_industries") or basic_info.get("industries")
    if isinstance(industries, list):
        return next((item.strip() for item in industries if isinstance(item, str) and item.strip()), None)
    return _text(industries)


def _unavailable_metrics():
    return CompanyMetrics(
        total_funding=UNAVAILABLE,
        last_round=UNAVAILABLE,
        last_round_date=UNAVAILABLE,
        valuation=UNAVAILABLE,
        employees="Not available",
        employee_growth=UNAVAILABLE,
        investors=[],
    )


class CompanyInfoStage(BasePipelineStage):
    @property
    def stage_id(self) -> str:
        return "company_info"

    @property
    def stage_name(self) -> str:
        return "Retrieving company information"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        company_id = context.crustdata_company_id
        if company_id is None:
            context.metrics = _unavailable_metrics()
            return context

        response = await crustdata_service.enrich_company(company_id)
        context.extra_data["crustdata_enrich_response"] = response
        matches = flatten_company_matches(response)
        matching = [
            match
            for match in matches
            if isinstance(match.get("company_data"), dict)
            and match["company_data"].get("crustdata_company_id") == company_id
        ]
        if len(matching) != 1:
            context.extra_data["company_enrichment_status"] = (
                "not_found" if not matches else "ambiguous_or_mismatched"
            )
            context.metrics = _unavailable_metrics()
            return context

        company_data = matching[0]["company_data"]
        context.extra_data["company_enrichment"] = company_data
        basic_info = company_data.get("basic_info") or {}
        funding = company_data.get("funding") or {}
        headcount = company_data.get("headcount") or {}
        locations = company_data.get("locations") or {}
        taxonomy = company_data.get("taxonomy") or {}
        market_intel = company_data.get("market_intel") or {}
        products = market_intel.get("products") or []
        market_sector = next(
            (
                _text(product.get("category"))
                for product in products
                if isinstance(product, dict) and _text(product.get("category"))
            ),
            None,
        ) if isinstance(products, list) else None

        if context.company_overview is not None:
            overview = context.company_overview
            round_type = _round_name(funding.get("last_round_type"))
            context.company_overview = overview.model_copy(
                update={
                    "name": _text(basic_info.get("name")) or overview.name,
                    "description": _text(basic_info.get("description")) or _text(market_intel.get("description")) or overview.description,
                    "sector": _industry(taxonomy, basic_info) or market_sector or overview.sector,
                    "stage": round_type or overview.stage,
                    "founded": _text(basic_info.get("year_founded")) or overview.founded,
                    "headquarters": _text(locations.get("headquarters")) or overview.headquarters,
                    "website": _text(market_intel.get("company_website_url"))
                    or _text(basic_info.get("website"))
                    or overview.website,
                }
            )

        round_type = _round_name(funding.get("last_round_type"))
        round_amount = _currency(funding.get("last_round_amount_usd"))
        if round_type and round_amount != UNAVAILABLE:
            last_round = f"{round_type} - {round_amount}"
        else:
            last_round = round_type or round_amount

        total_employees = headcount.get("total")
        if isinstance(total_employees, bool) or not isinstance(total_employees, (int, float)):
            total_employees = "Not available"
        else:
            total_employees = int(total_employees)

        growth_percent = headcount.get("growth_percent") or {}
        yoy_growth = growth_percent.get("yoy") if isinstance(growth_percent, dict) else None
        employee_growth = (
            f"{yoy_growth:+.1f}% YoY"
            if isinstance(yoy_growth, (int, float)) and not isinstance(yoy_growth, bool)
            else UNAVAILABLE
        )
        investors = funding.get("investors")

        context.metrics = CompanyMetrics(
            total_funding=_currency(funding.get("total_investment_usd")),
            last_round=last_round or UNAVAILABLE,
            last_round_date=_text(funding.get("last_fundraise_date")) or UNAVAILABLE,
            valuation=UNAVAILABLE,
            employees=total_employees,
            employee_growth=employee_growth,
            investors=[investor for investor in investors if isinstance(investor, str)]
            if isinstance(investors, list)
            else [],
        )
        context.extra_data["company_enrichment_status"] = "enriched"
        return context
