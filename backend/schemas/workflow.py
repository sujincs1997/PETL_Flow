from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

class NodeSchemaBase(BaseModel):
    node_key: str = Field(..., description="Unique key for node in React Flow canvas (e.g. node_1)")
    type: str = Field(..., description="Type of node matching python classes (e.g. CSVReader)")
    config: Dict[str, Any] = Field(default={}, description="Node parameters configuration")
    pos_x: float = 0.0
    pos_y: float = 0.0

class NodeSchemaCreate(NodeSchemaBase):
    pass

class NodeSchemaResponse(NodeSchemaBase):
    id: UUID

    class Config:
        from_attributes = True


class EdgeSchemaBase(BaseModel):
    source_node: str = Field(..., description="Source node key")
    target_node: str = Field(..., description="Target node key")
    source_handle: Optional[str] = "output"
    target_handle: Optional[str] = "input"

class EdgeSchemaCreate(EdgeSchemaBase):
    pass

class EdgeSchemaResponse(EdgeSchemaBase):
    id: UUID

    class Config:
        from_attributes = True


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: int = 1

class WorkflowCreate(WorkflowBase):
    nodes: List[NodeSchemaCreate] = []
    edges: List[EdgeSchemaCreate] = []

class WorkflowResponse(WorkflowBase):
    id: UUID
    is_active: bool
    owner_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    nodes: List[NodeSchemaResponse] = []
    edges: List[EdgeSchemaResponse] = []

    class Config:
        from_attributes = True


class CustomNodeBuilderSchema(BaseModel):
    type: str = Field(..., description="Unique snake_case or PascalCase type name")
    name: str = Field(..., description="Human readable display name")
    category: str = Field(default="Transformations", description="Category for node panel")
    description: str = Field(default="", description="Quick help label")
    code: str = Field(..., description="Python execute script body")
    parameters: List[Dict[str, Any]] = Field(default=[], description="Form parameter definitions")
