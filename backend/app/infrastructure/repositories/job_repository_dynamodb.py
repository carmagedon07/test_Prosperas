from typing import List, Optional
from uuid import UUID
import boto3
import os
from datetime import datetime
from ...domain.entities.job import Job
from ...domain.enums.job_status import JobStatus
from ...application.interfaces.job_repository import JobRepository


class JobRepositoryDynamoDB(JobRepository):
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://localstack:4566'),
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )
        self.table = self.dynamodb.Table(os.getenv('DYNAMODB_TABLE_NAME', 'jobs'))

    def create(self, job: Job) -> Job:
        item = {
            'job_id': str(job.job_id),
            'user_id': job.user_id,
            'status': job.status.value,
            'report_type': job.report_type,
            'date_range': job.date_range if job.date_range else None,
            'format': job.format,
            'created_at': job.created_at.isoformat() if job.created_at else datetime.utcnow().isoformat(),
            'updated_at': job.updated_at.isoformat() if job.updated_at else datetime.utcnow().isoformat(),
            'result_url': job.result_url if job.result_url else None,
            'error_msg': None
        }
        # Remove None values
        item = {k: v for k, v in item.items() if v is not None}
        self.table.put_item(Item=item)
        return job

    def get(self, job_id: UUID, user_id: str) -> Optional[Job]:
        response = self.table.get_item(Key={'job_id': str(job_id)})
        item = response.get('Item')
        if not item or item.get('user_id') != user_id:
            return None
        return self._to_domain(item)

    def list(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Job]:
        # Use GSI to query by user_id
        response = self.table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            Limit=limit + offset
        )
        items = response.get('Items', [])
        # Manual offset handling (DynamoDB doesn't have native offset)
        items = items[offset:offset + limit] if offset < len(items) else []
        return [self._to_domain(item) for item in items]

    def update(self, job: Job) -> Job:
        update_expr = "SET #status = :status, updated_at = :updated_at"
        expr_attr_names = {'#status': 'status'}
        expr_attr_values = {
            ':status': job.status.value,
            ':updated_at': datetime.utcnow().isoformat()
        }
        
        if job.result_url:
            update_expr += ", result_url = :result_url"
            expr_attr_values[':result_url'] = job.result_url
        
        if hasattr(job, 'error_msg') and job.error_msg:
            update_expr += ", error_msg = :error_msg"
            expr_attr_values[':error_msg'] = job.error_msg
        
        self.table.update_item(
            Key={'job_id': str(job.job_id)},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values
        )
        return job

    def update_status(self, job_id: UUID, status: JobStatus, result_url: Optional[str] = None, error_msg: Optional[str] = None) -> None:
        update_expr = "SET #status = :status, updated_at = :updated_at"
        expr_attr_names = {'#status': 'status'}
        expr_attr_values = {
            ':status': status.value,
            ':updated_at': datetime.utcnow().isoformat()
        }
        
        if result_url:
            update_expr += ", result_url = :result_url"
            expr_attr_values[':result_url'] = result_url
        
        if error_msg:
            update_expr += ", error_msg = :error_msg"
            expr_attr_values[':error_msg'] = error_msg
        
        self.table.update_item(
            Key={'job_id': str(job_id)},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values
        )

    def delete_all(self) -> int:
        """Delete all jobs from the table. Returns count of deleted items."""
        response = self.table.scan()
        items = response.get('Items', [])
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        count = 0
        for item in items:
            self.table.delete_item(Key={'job_id': item['job_id']})
            count += 1
        
        return count

    def _to_domain(self, item: dict) -> Job:
        return Job(
            job_id=UUID(item['job_id']),
            user_id=item['user_id'],
            status=JobStatus(item['status']),
            report_type=item['report_type'],
            date_range=item.get('date_range'),
            format=item['format'],
            created_at=datetime.fromisoformat(item['created_at']) if 'created_at' in item else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if 'updated_at' in item else None,
            result_url=item.get('result_url'),
            error_msg=item.get('error_msg')
        )
