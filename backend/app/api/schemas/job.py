from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from ...domain.enums.job_status import JobStatus

class JobCreateRequest(BaseModel):
    report_type: str = Field(...)

class JobResponse(BaseModel):
    job_id: UUID
    user_id: str
    status: JobStatus
    report_type: str
    created_at: datetime
    updated_at: datetime
    result_url: str | None = None
    
class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int | None = None
