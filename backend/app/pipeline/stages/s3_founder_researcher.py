"""Stage 3: infer founder candidates from current Crustdata employment titles."""

import re

from ..base import BasePipelineStage, PipelineContext
from ...services.crustdata import CrustdataServiceError, crustdata_service
from ...schemas.company import Founder


FOUNDER_TITLE = re.compile(r"\b(?:co[\s-]?founder|founder)\b", re.IGNORECASE)


def _current_employment(profile):
    experience = profile.get("experience") or {}
    employment = experience.get("employment_details") or {}
    current = employment.get("current") or []
    return [entry for entry in current if isinstance(entry, dict)] if isinstance(current, list) else []


def _previous_companies(profile, current_company_id):
    experience = profile.get("experience") or {}
    employment = experience.get("employment_details") or {}
    past = employment.get("past") or []
    if not isinstance(past, list):
        return []
    names = []
    for entry in past:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name") or entry.get("company_name")
        company_id = entry.get("crustdata_company_id") or entry.get("company_id")
        if (
            isinstance(name, str)
            and name.strip()
            and company_id != current_company_id
            and name.strip() not in names
        ):
            names.append(name.strip())
    return names[:5]


class FounderResearcherStage(BasePipelineStage):
    @property
    def stage_id(self) -> str:
        return "founders"

    @property
    def stage_name(self) -> str:
        return "Researching founders"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        context.founders = []
        if context.crustdata_company_id is None:
            context.extra_data["founder_research_status"] = "skipped_unverified_company"
            return context

        try:
            response = await crustdata_service.search_people(context.crustdata_company_id)
        except CrustdataServiceError as exc:
            context.extra_data["founder_research_status"] = "unavailable"
            context.extra_data["founder_research_error"] = str(exc)
            return context

        profiles = response.get("profiles", [])
        for profile in profiles:
            if not isinstance(profile, dict):
                continue
            basic_profile = profile.get("basic_profile") or {}
            title = basic_profile.get("current_title")
            current_roles = _current_employment(profile)
            if not isinstance(title, str) or not title.strip():
                title = next(
                    (role.get("title") for role in current_roles if isinstance(role.get("title"), str)),
                    "",
                )
            if not title or not FOUNDER_TITLE.search(title):
                continue

            name = basic_profile.get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            social_handles = profile.get("social_handles") or {}
            professional_network = social_handles.get("professional_network_identifier") or {}
            profile_url = professional_network.get("profile_url")
            current_role = next(
                (role for role in current_roles if role.get("title") == title),
                {},
            )
            role_company_id = current_role.get("crustdata_company_id") or current_role.get("company_id")
            if role_company_id is not None and str(role_company_id) != str(context.crustdata_company_id):
                continue

            context.founders.append(
                Founder(
                    name=name.strip(),
                    role=f"Inferred founder: {title.strip()}",
                    background=(
                        f"Inferred from a current Crustdata employment title ({title.strip()}); "
                        "the title is not independent verification of founder status."
                    ),
                    previous_companies=_previous_companies(profile, context.crustdata_company_id),
                    profile_url=profile_url if isinstance(profile_url, str) else "",
                )
            )

        context.extra_data["founder_research_status"] = "completed"
        context.extra_data["founder_search_total"] = response.get("total_count")
        return context
