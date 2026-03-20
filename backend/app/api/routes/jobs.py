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
    from datetime import datetime
    import boto3
    import os
    import json
    
    date_range = request.date_range or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job = create_job_use_case.execute(
        user_id=current_user["id"],
        report_type=request.report_type,
        date_range=date_range,
        format=request.format
    )
    
    # Publicar mensaje en SQS
    try:
        sqs = boto3.client(
            'sqs',
            endpoint_url=os.getenv('SQS_ENDPOINT', 'http://localstack:4566'),
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )
        
        queue_url_response = sqs.get_queue_url(QueueName=os.getenv('SQS_QUEUE_NAME', 'test-queue'))
        queue_url = queue_url_response['QueueUrl']
        
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

@router.get("/jobs", response_model=JobListResponse, dependencies=[Depends(require_admin)])
def list_jobs(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    jobs = list_jobs_use_case.execute(user_id=current_user["id"], limit=limit, offset=offset)
    jobs_list = [JobResponse(**job.__dict__) for job in jobs] if jobs else []
    return JobListResponse(jobs=jobs_list)

@router.delete("/jobs", status_code=200, dependencies=[Depends(require_admin)])
def delete_all_jobs(current_user: dict = Depends(get_current_user)):
    """Delete all jobs from DynamoDB. Requires admin privileges."""
    count = delete_all_jobs_use_case.execute()
    return {"message": f"Successfully deleted {count} jobs", "count": count}
