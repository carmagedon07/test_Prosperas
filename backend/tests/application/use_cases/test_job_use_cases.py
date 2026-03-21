import pytest
from uuid import uuid4, UUID
from unittest.mock import Mock
from app.application.use_cases.create_job import CreateJobUseCase
from app.application.use_cases.get_job import GetJobUseCase
from app.application.use_cases.update_job_status import UpdateJobStatusUseCase
from app.domain.entities.job import Job
from app.domain.enums.job_status import JobStatus

@pytest.fixture
def job_repository_mock():
    return Mock()

def test_create_job_sets_pending(job_repository_mock):
    # Arrange
    use_case = CreateJobUseCase(job_repository_mock)
    user_id = "user-1"
    report_type = "ventas"
    date_range = "2024-01"
    format = "PDF"
    # Simula que el repo devuelve el mismo job
    job_repository_mock.create.side_effect = lambda job: job
    # Act
    job = use_case.execute(user_id=user_id, report_type=report_type, date_range=date_range, format=format)
    # Assert
    assert job.status == JobStatus.PENDING
    assert job.user_id == user_id
    assert job.report_type == report_type
    assert isinstance(job.job_id, UUID)
    job_repository_mock.create.assert_called_once()

def test_get_job_success(job_repository_mock):
    # Arrange
    job_id = uuid4()
    user_id = "user-2"
    job = Job(user_id=user_id, report_type="ventas", date_range="2024-01", format="PDF", job_id=job_id)
    job_repository_mock.get.return_value = job
    use_case = GetJobUseCase(job_repository_mock)
    # Act
    result = use_case.execute(job_id=job_id, user_id=user_id)
    # Assert
    assert result == job
    job_repository_mock.get.assert_called_once_with(job_id, user_id)

def test_get_job_not_found_raises(job_repository_mock):
    # Arrange
    job_repository_mock.get.return_value = None
    use_case = GetJobUseCase(job_repository_mock)
    # Act & Assert
    with pytest.raises(ValueError):
        use_case.execute(job_id=uuid4(), user_id="no-user")

def test_update_job_status_transitions(job_repository_mock):
    # Arrange
    use_case = UpdateJobStatusUseCase(job_repository_mock)
    job_id = uuid4()
    # Act
    use_case.execute(job_id, JobStatus.PROCESSING)
    use_case.execute(job_id, JobStatus.COMPLETED, result_url="url")
    use_case.execute(job_id, JobStatus.FAILED, error_msg="fail")
    # Assert
    assert job_repository_mock.update_status.call_count == 3
    job_repository_mock.update_status.assert_any_call(job_id, JobStatus.PROCESSING, None, None)
    job_repository_mock.update_status.assert_any_call(job_id, JobStatus.COMPLETED, "url", None)
    job_repository_mock.update_status.assert_any_call(job_id, JobStatus.FAILED, None, "fail")
