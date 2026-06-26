from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db, GUID
from ..models.execution import Execution
from ..models.workflow import Workflow
from ..schemas.execution import ExecutionResponse, ExecutionDetailResponse
from ..api.auth import get_current_user, RoleChecker
from ..models.user import User
from ..engine.tasks import execute_workflow_task, run_workflow_execution
from ..config import settings
from typing import List
from uuid import UUID
import json
import os

router = APIRouter(prefix="/executions", tags=["executions"])

check_analyst_or_above = RoleChecker(["Admin", "Developer", "Analyst"])
check_viewer_or_above = RoleChecker(["Admin", "Developer", "Analyst", "Viewer"])

@router.post("/run/{workflow_id}", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def run_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    debug_mode: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_analyst_or_above)
):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.is_active == True).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found or inactive.")

    # Create Execution record
    execution = Execution(
        workflow_id=workflow.id,
        status="PENDING",
        triggered_by=current_user.id
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Attempt Celery run only if enabled; otherwise use background thread directly
    if settings.USE_CELERY:
        try:
            execute_workflow_task.delay(str(execution.id), debug_mode)
        except Exception as e:
            background_tasks.add_task(run_workflow_execution, str(execution.id), debug_mode)
    else:
        # Fast local execution thread without Redis timeout delays
        background_tasks.add_task(run_workflow_execution, str(execution.id), debug_mode)

    return execution

@router.get("/{execution_id}", response_model=ExecutionDetailResponse)
def get_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_viewer_or_above)
):
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found.")
    return execution

@router.get("/{execution_id}/inspection/{node_key}")
def get_inspection_report(
    execution_id: str,
    node_key: str,
    current_user: User = Depends(check_viewer_or_above)
):
    """Retrieve the Inspector node's JSON report for a given execution and node."""
    report_path = os.path.join(
        settings.INTERMEDIATE_STORAGE_PATH,
        execution_id,
        f"{node_key}_inspection.json"
    )
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail=f"Inspection report not found for node '{node_key}' in execution '{execution_id}'.")

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    return JSONResponse(content=report)

@router.get("/workflow/{workflow_id}", response_model=List[ExecutionResponse])
def get_workflow_executions(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_viewer_or_above)
):
    return db.query(Execution).filter(Execution.workflow_id == workflow_id).order_by(Execution.started_at.desc()).all()

