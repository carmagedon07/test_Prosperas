from typing import List, Optional, Tuple
from uuid import UUID
from ...domain.entities.job import Job
from ...domain.enums.job_status import JobStatus

class JobRepository:
    def create(self, job: Job) -> Job:
        raise NotImplementedError

    def get(self, job_id: UUID, user_id: str) -> Optional[Job]:
        raise NotImplementedError

    def list(self, user_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[Job], int]:
        """Returns (items, total_count) for the given page."""
        raise NotImplementedError

    def update_status(self, job_id: UUID, status: JobStatus, result_url: Optional[str] = None, error_msg: Optional[str] = None) -> None:
        raise NotImplementedError

    def delete_all(self) -> int:
        """Delete all jobs. Returns count of deleted items."""
        raise NotImplementedError
