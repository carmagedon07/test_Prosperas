from typing import List, Optional
from uuid import UUID
from ...domain.entities.job import Job
from ...domain.enums.job_status import JobStatus

class JobRepository:
    def create(self, job: Job) -> Job:
        raise NotImplementedError

    def get(self, job_id: UUID, user_id: str) -> Optional[Job]:
        raise NotImplementedError

    def list(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Job]:
        raise NotImplementedError

    def update_status(self, job_id: UUID, status: JobStatus, result_url: Optional[str] = None, error_msg: Optional[str] = None) -> None:
        raise NotImplementedError
