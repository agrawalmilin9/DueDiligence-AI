from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from ...pipeline.orchestrator import orchestrator
from ...schemas.common import InvestigationStatus
from ...schemas.investigation import (
    InvestigationCreateRequest,
    InvestigationRecord,
    InvestigationSummary,
)
from ...schemas.report import InvestigationReport
from ...services.storage import investigation_store

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.post(
    "",
    response_model=InvestigationRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Create and start a new investigation",
)
async def create_investigation(
    payload: InvestigationCreateRequest,
    background_tasks: BackgroundTasks,
    run_sync: bool = Query(
        True,
        alias="sync",
        description="Run pipeline synchronously (True) or asynchronously in background (False)",
    ),
):
    """
    Initiate a due diligence investigation for a given startup name and mandate.
    Transitions through 7 research stages with status tracking:
    'pending' -> 'running' -> 'completed' (or 'failed').
    """
    company_name = payload.company_name.strip()
    if not company_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Startup name cannot be empty.",
        )

    investigation_request = (
        payload.request.strip()
        if payload.request and payload.request.strip()
        else "Analyze this startup for a potential investment of $2M."
    )

    # Initialize record in storage with status = PENDING
    record = investigation_store.create(
        company_name=company_name,
        request=investigation_request,
    )

    if run_sync:
        # Run immediately in-request
        await orchestrator.run(
            investigation_id=record.id,
            company_name=record.company_name,
            request=record.request,
        )
        updated_record = investigation_store.get(record.id)
        return updated_record or record
    else:
        # Enqueue background execution for polling
        background_tasks.add_task(
            orchestrator.run,
            investigation_id=record.id,
            company_name=record.company_name,
            request=record.request,
        )
        return record


@router.get(
    "",
    response_model=List[InvestigationSummary],
    summary="List all recent investigations",
)
async def list_investigations():
    """
    Retrieve summaries of all recorded investigations.
    """
    return investigation_store.list_summaries()


@router.get(
    "/{investigation_id}",
    response_model=InvestigationRecord,
    summary="Get investigation record by ID with status tracking",
)
async def get_investigation(investigation_id: str):
    """
    Retrieve an investigation record including current status (pending, running,
    completed, failed), active progress step, and full report if completed.
    """
    record = investigation_store.get(investigation_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' not found.",
        )
    return record


@router.get(
    "/{investigation_id}/report",
    response_model=InvestigationReport,
    summary="Get direct InvestigationReport for frontend drop-in compatibility",
)
async def get_investigation_report(investigation_id: str):
    """
    Returns the exact InvestigationReport schema for 1:1 integration
    with the frontend getInvestigationReport() data layer.
    """
    record = investigation_store.get(investigation_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' not found.",
        )

    if record.status == InvestigationStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {record.error or 'Unknown pipeline error'}",
        )

    if not record.report or record.status != InvestigationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Report is not ready yet. Current status: '{record.status}', step: '{record.current_step}'.",
        )

    return record.report
