import pytest
from uuid import UUID
from app.application.use_cases.create_job import CreateJobUseCase
from app.domain.entities.job import Job

class FakeJobRepository:
    def __init__(self):
        self.created = []
    def create(self, job):
        self.created.append(job)
        return job

@pytest.fixture
def fake_repo():
    return FakeJobRepository()

def test_create_job_success(fake_repo):
    use_case = CreateJobUseCase(fake_repo)
    user_id = "user-123"
    report_type = "ventas"
    date_range = "2024-01"
    format = "PDF"
    job = use_case.execute(user_id=user_id, report_type=report_type, date_range=date_range, format=format)
    assert job.user_id == user_id
    assert job.report_type == report_type
    assert job.status.value == "PENDING"
    assert isinstance(job.job_id, UUID)
    assert fake_repo.created[0] == job
