from sqlalchemy import Column, Integer, String, JSON, Boolean
from ..database import Base

class AttributeDef(Base):
    __tablename__ = "attribute_def"
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False, comment="Target database table name")
    pk_column = Column(String, nullable=False, comment="Primary key column name for the table")
    field_name = Column(String, nullable=False, comment="Column/field name being edited")
    field_type = Column(String, nullable=False, comment="Data type: string, integer, decimal, enum, date, etc.")
    validation_json = Column(JSON, nullable=True, comment="JSON Schema fragment for validation rules")
    # optional description
    description = Column(String, nullable=True)
