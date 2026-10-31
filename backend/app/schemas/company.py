from typing import List, Literal
from .base import CamelModel
from .common import RiskLevel


class CompanyOverview(CamelModel):
    name: str
    tagline: str
    description: str
    sector: str
    stage: str
    founded: str
    headquarters: str
    website: str
    business_model: str


class CompanyMetrics(CamelModel):
    total_funding: str
    last_round: str
    last_round_date: str
    valuation: str
    employees: int | str
    employee_growth: str
    investors: List[str]


class Founder(CamelModel):
    name: str
    role: str
    background: str
    previous_companies: List[str]
    profile_url: str


class Competitor(CamelModel):
    name: str
    description: str
    funding: str
    positioning: Literal["Leader", "Challenger", "Niche"]
    threat: RiskLevel
