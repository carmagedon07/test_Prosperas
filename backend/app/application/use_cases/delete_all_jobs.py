from ...application.interfaces.job_repository import JobRepository


class DeleteAllJobsUseCase:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def execute(self) -> int:
        """Delete all jobs. Returns the count of deleted items."""
        return self.job_repository.delete_all()
