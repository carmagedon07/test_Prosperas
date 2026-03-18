from datetime import datetime
from uuid import UUID, uuid4
from ..enums.job_status import JobStatus

class Job:
    def __init__(
        self,
        user_id: str,
        report_type: str,
        status: JobStatus = JobStatus.PENDING,
        created_at: datetime = None,
        updated_at: datetime = None,
        result_url: str = None,
        job_id: UUID = None,
    ):
        self.job_id = job_id or uuid4()
        self.user_id = user_id
        self.status = status
        self.report_type = report_type
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at
        self.result_url = result_url
