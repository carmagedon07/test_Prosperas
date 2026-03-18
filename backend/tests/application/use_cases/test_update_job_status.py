import pytest
from uuid import uuid4
from app.application.use_cases.update_job_status import UpdateJobStatusUseCase
from app.domain.enums.job_status import JobStatus

class FakeJobRepository:
    def __init__(self):
        self.updated = []
    def update_status(self, job_id, status, result_url=None, error_msg=None):
        self.updated.append((job_id, status, result_url, error_msg))

@pytest.fixture
def fake_repo():
    return FakeJobRepository()

def test_update_job_status_success(fake_repo):
    use_case = UpdateJobStatusUseCase(fake_repo)
    job_id = uuid4()
    use_case.execute(job_id, JobStatus.PROCESSING, result_url="url", error_msg=None)
    assert fake_repo.updated[0] == (job_id, JobStatus.PROCESSING, "url", None)

