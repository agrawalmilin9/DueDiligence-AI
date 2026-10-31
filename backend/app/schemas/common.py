from enum import Enum
from .base import CamelModel


class ClaimStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTING = "CONFLICTING"


class Recommendation(str, Enum):
    PROCEED = "PROCEED"
    PROCEED_WITH_CAUTION = "PROCEED_WITH_CAUTION"
    AVOID = "AVOID"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class InvestigationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Source(CamelModel):
    title: str
    url: str
