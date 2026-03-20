from ...application.interfaces.job_repository import JobRepository
from ...domain.entities.job import Job
from typing import List, Tuple

class ListJobsUseCase:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def execute(self, user_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[Job], int]:
        """Returns (jobs, total_count) for the requested page."""
        return self.job_repository.list(user_id, page=page, page_size=page_size)
