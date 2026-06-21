from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.workflow import Workflow, Node, Edge
from ..schemas.workflow import WorkflowCreate, WorkflowResponse
from ..api.auth import get_current_user, RoleChecker
from ..models.user import User
from typing import List
from uuid import UUID

router = APIRouter(prefix="/workflows", tags=["workflows"])

# RBAC Guards
check_developer_or_admin = RoleChecker(["Admin", "Developer"])
check_analyst_or_above = RoleChecker(["Admin", "Developer", "Analyst"])
check_viewer_or_above = RoleChecker(["Admin", "Developer", "Analyst", "Viewer"])

@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    workflow_in: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_developer_or_admin)
):
    # Create workflow entry
    db_workflow = Workflow(
        name=workflow_in.name,
        description=workflow_in.description,
        version=workflow_in.version,
        owner_id=current_user.id
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)

    # Create associated nodes
    for node_data in workflow_in.nodes:
        db_node = Node(
            workflow_id=db_workflow.id,
            node_key=node_data.node_key,
            type=node_data.type,
            config=node_data.config,
            pos_x=node_data.pos_x,
            pos_y=node_data.pos_y
        )
        db.add(db_node)

    # Create associated edges
    for edge_data in workflow_in.edges:
        db_edge = Edge(
            workflow_id=db_workflow.id,
            source_node=edge_data.source_node,
            target_node=edge_data.target_node,
            source_handle=edge_data.source_handle,
            target_handle=edge_data.target_handle
        )
        db.add(db_edge)

    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.get("", response_model=List[WorkflowResponse])
def get_workflows(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_viewer_or_above)
):
    return db.query(Workflow).filter(Workflow.is_active == True).all()

@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_viewer_or_above)
):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.is_active == True).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: str,
    workflow_in: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_developer_or_admin)
):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    # Update basic details
    workflow.name = workflow_in.name
    workflow.description = workflow_in.description
    workflow.version += 1
    
    # Remove existing nodes & edges
    db.query(Node).filter(Node.workflow_id == workflow_id).delete()
    db.query(Edge).filter(Edge.workflow_id == workflow_id).delete()

    # Re-insert nodes
    for node_data in workflow_in.nodes:
        db_node = Node(
            workflow_id=workflow_id,
            node_key=node_data.node_key,
            type=node_data.type,
            config=node_data.config,
            pos_x=node_data.pos_x,
            pos_y=node_data.pos_y
        )
        db.add(db_node)

    # Re-insert edges
    for edge_data in workflow_in.edges:
        db_edge = Edge(
            workflow_id=workflow_id,
            source_node=edge_data.source_node,
            target_node=edge_data.target_node,
            source_handle=edge_data.source_handle,
            target_handle=edge_data.target_handle
        )
        db.add(db_edge)

    db.commit()
    db.refresh(workflow)
    return workflow

@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_developer_or_admin)
):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    
    # Soft delete
    workflow.is_active = False
    db.commit()
    return None
