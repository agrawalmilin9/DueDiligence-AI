"""
Pipeline Orchestrator
---------------------
Coordinates the sequential execution of all 7 due diligence research stages:
1. Company identification
2. Company information retrieval
3. Founder identification and research
4. Market and competitor research
5. Claim verification
6. Risk analysis
7. Investment report generation

Updates investigation status and progress steps throughout execution.
"""

import logging
from typing import List, Optional
from datetime import datetime, timezone

from .base import BasePipelineStage, PipelineContext
from .stages import (
    CompanyIdentifierStage,
    CompanyInfoStage,
    FounderResearcherStage,
    MarketResearcherStage,
    ClaimVerifierStage,
    RiskAnalyzerStage,
    ReportGeneratorStage,
)
from ..schemas.common import InvestigationStatus
from ..schemas.report import InvestigationReport
from ..services.storage import investigation_store

logger = logging.getLogger(__name__)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PipelineOrchestrator:
    def __init__(self, stages: Optional[List[BasePipelineStage]] = None):
        self.stages = stages or [
            CompanyIdentifierStage(),
            CompanyInfoStage(),
            FounderResearcherStage(),
            MarketResearcherStage(),
            ClaimVerifierStage(),
            RiskAnalyzerStage(),
            ReportGeneratorStage(),
        ]

    async def run(
        self,
        investigation_id: str,
        company_name: str,
        request: str,
    ) -> InvestigationReport:
        """
        Executes the 7 pipeline stages sequentially, transitioning status from
        pending -> running (per-step) -> completed (or failed).
        """
        logger.info(f"Starting investigation pipeline for '{company_name}' (ID: {investigation_id})")

        investigation_store.update_status(
            investigation_id=investigation_id,
            status=InvestigationStatus.RUNNING,
            current_step="starting",
        )

        context = PipelineContext(
            investigation_id=investigation_id,
            company_name=company_name,
            request=request,
        )

        try:
            for stage in self.stages:
                investigation_store.update_status(
                    investigation_id=investigation_id,
                    status=InvestigationStatus.RUNNING,
                    current_step=stage.stage_id,
                )
                logger.info(f"[{investigation_id}] Running stage: {stage.stage_id} - {stage.stage_name}")
                context = await stage.execute(context)

            # Compile into finalized report
            report = context.to_report(generated_at=utc_now_iso())
            investigation_store.set_report(investigation_id=investigation_id, report=report)
            logger.info(f"[{investigation_id}] Pipeline completed successfully")
            return report

        except Exception as exc:
            error_msg = f"Pipeline execution failed at step '{context.extra_data.get('last_step', 'unknown')}': {str(exc)}"
            logger.error(f"[{investigation_id}] {error_msg}", exc_info=True)
            investigation_store.update_status(
                investigation_id=investigation_id,
                status=InvestigationStatus.FAILED,
                error=error_msg,
            )
            raise exc


# Shared orchestrator instance
orchestrator = PipelineOrchestrator()
