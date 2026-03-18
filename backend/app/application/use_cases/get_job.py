from uuid import UUID
from ...application.interfaces.job_repository import JobRepository
from ...domain.entities.job import Job

class GetJobUseCase:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def execute(self, job_id: UUID, user_id: str) -> Job:
        job = self.job_repository.get(job_id, user_id)
        if not job:
            raise ValueError("Job not found")
        return job
