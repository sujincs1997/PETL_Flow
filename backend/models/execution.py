import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base, GUID

class Execution(Base):
    __tablename__ = "executions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workflow_id = Column(GUID, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    triggered_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    workflow = relationship("Workflow", back_populates="executions")
    user = relationship("User")
    logs = relationship("Log", back_populates="execution", cascade="all, delete-orphan")


class Log(Base):
    __tablename__ = "logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    execution_id = Column(GUID, ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    node_key = Column(String, nullable=True) # node ID on the canvas, can be null for general logs
    log_level = Column(String, default="INFO") # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    execution = relationship("Execution", back_populates="logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False) # e.g. "CREATE_WORKFLOW", "RUN_WORKFLOW"
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
