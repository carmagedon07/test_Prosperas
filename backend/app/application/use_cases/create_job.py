from ...domain.entities.job import Job
from ...application.interfaces.job_repository import JobRepository

class CreateJobUseCase:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def execute(self, user_id: str, report_type: str, date_range: str, format: str) -> Job:
        job = Job(user_id=user_id, report_type=report_type, date_range=date_range, format=format)
        return self.job_repository.create(job)
