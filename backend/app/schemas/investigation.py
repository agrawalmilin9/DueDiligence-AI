from typing import Optional
from pydantic import Field, model_validator
from .base import CamelModel
from .common import InvestigationStatus, Recommendation
from .report import InvestigationReport


class InvestigationCreateRequest(CamelModel):
    company_name: str = Field(..., description="Startup or target company name")
    request: Optional[str] = Field(
        default="Analyze this startup for a potential investment of $2M.",
        description="Investigation mandate or specific prompt",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_company_input(cls, data):
        if isinstance(data, dict):
            # Allow 'company' as an alias for 'companyName' or 'company_name'
            if "company" in data and "company_name" not in data and "companyName" not in data:
                data["company_name"] = data["company"]
        return data


class InvestigationSummary(CamelModel):
    id: str
    company_name: str
    sector: str
    request: str
    created_at: str
    verdict: Recommendation
    score: int


class InvestigationRecord(CamelModel):
    id: str
    company_name: str
    request: str
    status: InvestigationStatus
    current_step: Optional[str] = None
    created_at: str
    updated_at: str
    report: Optional[InvestigationReport] = None
    error: Optional[str] = None
