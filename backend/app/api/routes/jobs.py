from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from ...api.schemas.job import JobCreateRequest, JobResponse, JobListResponse
from ...application.use_cases.create_job import CreateJobUseCase
from ...application.use_cases.get_job import GetJobUseCase
from ...application.use_cases.list_jobs import ListJobsUseCase
from ...application.use_cases.delete_all_jobs import DeleteAllJobsUseCase
from ...infrastructure.repositories.job_repository_dynamodb import JobRepositoryDynamoDB
from ..dependencies import get_current_user, require_admin

router = APIRouter()

# Dependency injection
job_repository = JobRepositoryDynamoDB()
create_job_use_case = CreateJobUseCase(job_repository)
get_job_use_case = GetJobUseCase(job_repository)
list_jobs_use_case = ListJobsUseCase(job_repository)
delete_all_jobs_use_case = DeleteAllJobsUseCase(job_repository)

@router.post("/jobs", response_model=JobResponse, status_code=201)
def create_job(
    request: JobCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    import boto3
    import os
    import json
    
    job = create_job_use_case.execute(
        user_id=current_user["id"],
        report_type=request.report_type,
        date_range=request.date_range,
        format=request.format
    )
    
    # Publicar mensaje en SQS
    try:
        sqs = boto3.client(
            'sqs',
            endpoint_url=os.getenv('SQS_ENDPOINT') or None,
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )

        queue_url = os.getenv('SQS_QUEUE_URL') or \
            sqs.get_queue_url(QueueName=os.getenv('SQS_QUEUE_NAME', 'jobs-queue'))['QueueUrl']
        
        message = {
            'job_id': str(job.job_id),
            'user_id': job.user_id,
            'report_type': job.report_type
        }
        
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )
        print(f"[BACKEND] Mensaje publicado en SQS para job_id: {job.job_id}")
    except Exception as e:
        print(f"[BACKEND ERROR] Error al publicar en SQS: {e}")
    
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

@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (min 20 recommended)")
):
    import math
    jobs, total = list_jobs_use_case.execute(
        user_id=current_user["id"], page=page, page_size=page_size
    )
    jobs_list = [JobResponse(**job.__dict__) for job in jobs]
    total_pages = math.ceil(total / page_size) if page_size else 1
    return JobListResponse(
        jobs=jobs_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(total_pages, 1)
    )

@router.delete("/jobs", status_code=200, dependencies=[Depends(require_admin)])
def delete_all_jobs(current_user: dict = Depends(get_current_user)):
    """Delete all jobs from DynamoDB. Requires admin privileges."""
    count = delete_all_jobs_use_case.execute()
    return {"message": f"Successfully deleted {count} jobs", "count": count}
