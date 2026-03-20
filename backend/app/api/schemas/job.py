from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from ...domain.enums.job_status import JobStatus

from typing import Optional

class JobCreateRequest(BaseModel):
    report_type: str = Field(...)
    date_range: str = Field(..., description="Date range in format: YYYY-MM-DD to YYYY-MM-DD")
    format: str = Field(...)

class JobResponse(BaseModel):
    job_id: UUID
    user_id: str
    status: JobStatus
    report_type: str
    date_range: str
    format: str
    created_at: datetime
    updated_at: datetime
    result_url: str | None = None
    
class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int | None = None
