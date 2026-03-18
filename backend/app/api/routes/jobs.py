from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from ...api.schemas.job import JobCreateRequest, JobResponse, JobListResponse
from ...application.use_cases.create_job import CreateJobUseCase
from ...application.use_cases.get_job import GetJobUseCase
from ...application.use_cases.list_jobs import ListJobsUseCase
from ...infrastructure.repositories.job_repository_sqlalchemy import JobRepositorySQLAlchemy
from ..dependencies import get_current_user, require_admin

router = APIRouter()

# Dependency injection
job_repository = JobRepositorySQLAlchemy()
create_job_use_case = CreateJobUseCase(job_repository)
get_job_use_case = GetJobUseCase(job_repository)
list_jobs_use_case = ListJobsUseCase(job_repository)

@router.post("/jobs", response_model=JobResponse, status_code=201)
def create_job(
    request: JobCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    job = create_job_use_case.execute(user_id=current_user["id"], report_type=request.report_type)
    return JobResponse(**job.__dict__)

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    try:
        job = get_job_use_case.execute(job_id=job_id, user_id=current_user["id"])
        return JobResponse(**job.__dict__)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")

@router.get("/jobs", response_model=JobListResponse, dependencies=[Depends(require_admin)])
def list_jobs(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    jobs = list_jobs_use_case.execute(user_id=current_user["id"], limit=limit, offset=offset)
    return JobListResponse(jobs=[JobResponse(**job.__dict__) for job in jobs])
