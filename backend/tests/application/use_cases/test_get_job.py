import pytest
from uuid import uuid4
from app.application.use_cases.get_job import GetJobUseCase
from app.domain.entities.job import Job
from app.domain.enums.job_status import JobStatus

class FakeJobRepository:
    def __init__(self, jobs=None):
        self.jobs = jobs or {}
    def get(self, job_id, user_id):
        return self.jobs.get((str(job_id), user_id))

@pytest.fixture
def fake_repo():
    job = Job(user_id="user-1", report_type="ventas", job_id=uuid4())
    repo = FakeJobRepository({(str(job.job_id), job.user_id): job})
    return repo, job

def test_get_job_success(fake_repo):
    repo, job = fake_repo
    use_case = GetJobUseCase(repo)
    result = use_case.execute(job_id=job.job_id, user_id=job.user_id)
    assert result == job

def test_get_job_not_found(fake_repo):
    repo, job = fake_repo
    use_case = GetJobUseCase(repo)
    with pytest.raises(ValueError):
        use_case.execute(job_id=uuid4(), user_id="other-user")
