from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ...domain.entities.job import Job
from ...domain.enums.job_status import JobStatus
from ...application.interfaces.job_repository import JobRepository
from ..db.models import JobModel
from ..db.session import SessionLocal
from datetime import datetime

class JobRepositorySQLAlchemy(JobRepository):
    def __init__(self, db_session_factory=SessionLocal):
        self.db_session_factory = db_session_factory

    def create(self, job: Job) -> Job:
        with self.db_session_factory() as db:
            db_job = JobModel(
                job_id=str(job.job_id),
                user_id=job.user_id,
                status=job.status,
                report_type=job.report_type,
                created_at=job.created_at,
                updated_at=job.updated_at,
                result_url=job.result_url,
            )
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
            return self._to_domain(db_job)

    def get(self, job_id: UUID, user_id: str) -> Optional[Job]:
        with self.db_session_factory() as db:
            db_job = db.query(JobModel).filter_by(job_id=str(job_id), user_id=user_id).first()
            return self._to_domain(db_job) if db_job else None

    def list(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Job]:
        with self.db_session_factory() as db:
            db_jobs = db.query(JobModel).filter_by(user_id=user_id).order_by(JobModel.created_at.desc()).offset(offset).limit(limit).all()
            return [self._to_domain(j) for j in db_jobs]

    def update_status(self, job_id: UUID, status: JobStatus, result_url: Optional[str] = None, error_msg: Optional[str] = None) -> None:
        with self.db_session_factory() as db:
            db_job = db.query(JobModel).filter_by(job_id=str(job_id)).first()
            if db_job:
                db_job.status = status
                db_job.updated_at = datetime.utcnow()
                if result_url:
                    db_job.result_url = result_url
                if error_msg:
                    db_job.error_msg = error_msg
                db.commit()

    def _to_domain(self, db_job: JobModel) -> Job:
        return Job(
            job_id=db_job.job_id,
            user_id=db_job.user_id,
            status=db_job.status,
            report_type=db_job.report_type,
            created_at=db_job.created_at,
            updated_at=db_job.updated_at,
            result_url=db_job.result_url,
        )
