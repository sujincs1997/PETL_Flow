import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from ..database import Base, GUID

class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="Analyst") # Admin, Developer, Analyst, Viewer
    created_at = Column(DateTime, default=datetime.utcnow)
