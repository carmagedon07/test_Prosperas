from ...application.interfaces.job_repository import JobRepository
from ...domain.entities.job import Job
from typing import List

class ListJobsUseCase:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def execute(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Job]:
        return self.job_repository.list(user_id, limit, offset)
