from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class CustomNode(Base):
    __tablename__ = "custom_nodes"
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, unique=True, nullable=False, comment="Unique node type identifier")
    display_name = Column(String, nullable=False, comment="Name shown in UI")
    description = Column(String, nullable=True)
    parameters_schema = Column(JSON, nullable=False, comment="JSON Schema describing node parameters")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
