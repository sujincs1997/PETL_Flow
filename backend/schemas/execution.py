from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class LogResponse(BaseModel):
    id: UUID
    node_key: Optional[str] = None
    log_level: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ExecutionResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    triggered_by: Optional[UUID] = None

    class Config:
        from_attributes = True

class ExecutionDetailResponse(ExecutionResponse):
    logs: List[LogResponse] = []

    class Config:
        from_attributes = True
