import threading
import time
import random
from uuid import UUID
from app.application.use_cases.update_job_status import UpdateJobStatusUseCase
from app.domain.enums.job_status import JobStatus
from app.infrastructure.repositories.job_repository_sqlalchemy import JobRepositorySQLAlchemy

def process_job(job_id: UUID):
    job_repository = JobRepositorySQLAlchemy()
    update_status_use_case = UpdateJobStatusUseCase(job_repository)
    try:
        update_status_use_case.execute(job_id, JobStatus.PROCESSING)
        time.sleep(random.randint(5, 15))
        # Simular resultado
        result_url = f"https://dummy.result/{job_id}"
        update_status_use_case.execute(job_id, JobStatus.COMPLETED, result_url=result_url)
    except Exception as e:
        update_status_use_case.execute(job_id, JobStatus.FAILED, error_msg=str(e))

def start_fake_worker(job_id: UUID):
    thread = threading.Thread(target=process_job, args=(job_id,))
    thread.daemon = True
    thread.start()
