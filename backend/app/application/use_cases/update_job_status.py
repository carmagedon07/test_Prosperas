from uuid import UUID
from ...application.interfaces.job_repository import JobRepository
from ...domain.enums.job_status import JobStatus
from typing import Optional

class UpdateJobStatusUseCase:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def execute(self, job_id: UUID, status: JobStatus, result_url: Optional[str] = None, error_msg: Optional[str] = None):
        self.job_repository.update_status(job_id, status, result_url, error_msg)
