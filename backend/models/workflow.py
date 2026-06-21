import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from ..database import Base, GUID

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    owner_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User")
    nodes = relationship("Node", back_populates="workflow", cascade="all, delete-orphan", lazy="selectin")
    edges = relationship("Edge", back_populates="workflow", cascade="all, delete-orphan", lazy="selectin")
    executions = relationship("Execution", back_populates="workflow", cascade="all, delete-orphan")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workflow_id = Column(GUID, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    node_key = Column(String, nullable=False) # e.g. 'node_1' on frontend canvas
    type = Column(String, nullable=False)      # e.g. 'CSVReader', 'Buffer'
    config = Column(JSON, default={}, nullable=False) # parameters
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)

    workflow = relationship("Workflow", back_populates="nodes")


class Edge(Base):
    __tablename__ = "edges"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workflow_id = Column(GUID, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    source_node = Column(String, nullable=False) # node_key of source
    target_node = Column(String, nullable=False) # node_key of target
    source_handle = Column(String, default="output", nullable=True)
    target_handle = Column(String, default="input", nullable=True)

    workflow = relationship("Workflow", back_populates="edges")
