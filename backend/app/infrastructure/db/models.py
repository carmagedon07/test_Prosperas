from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import CHAR
from sqlalchemy.sql import func
from uuid import uuid4
from ...domain.enums.job_status import JobStatus
from .session import Base

class JobModel(Base):
    __tablename__ = "jobs"
    job_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False)
    status = Column(SAEnum(JobStatus), nullable=False)
    report_type = Column(String, nullable=False)
    date_range = Column(String, nullable=False)
    format = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    result_url = Column(String, nullable=True)
    error_msg = Column(String, nullable=True)
