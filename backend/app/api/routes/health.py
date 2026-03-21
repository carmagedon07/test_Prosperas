from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import boto3
import os
from botocore.exceptions import ClientError

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint con validación de dependencias críticas.
    
    Verifica:
    - DynamoDB: tabla de jobs accesible
    - SQS: cola de mensajes accesible
    
    Responde:
    - 200 si todos los checks pasan
    - 503 si algún check falla (para que ALB lo marque unhealthy)
    """
    checks = {
        "service": "backend",
        "status": "healthy",
        "checks": {}
    }
    
    all_healthy = True
    
    # Check 1: DynamoDB
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            endpoint_url=os.getenv('DYNAMODB_ENDPOINT') or None,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID') if os.getenv('DYNAMODB_ENDPOINT') else None,
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY') if os.getenv('DYNAMODB_ENDPOINT') else None,
        )
        table_name = os.getenv('DYNAMODB_TABLE_NAME', 'jobs')
        table = dynamodb.Table(table_name)
        
        # Intentar describir la tabla (no hace scan, solo metadata)
        table.load()
        
        checks["checks"]["dynamodb"] = {
            "status": "healthy",
            "table": table_name,
            "item_count": table.item_count if hasattr(table, 'item_count') else "N/A"
        }
    except ClientError as e:
        all_healthy = False
        checks["checks"]["dynamodb"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    except Exception as e:
        all_healthy = False
        checks["checks"]["dynamodb"] = {
            "status": "unhealthy",
            "error": f"Unexpected error: {str(e)}"
        }
    
    # Check 2: SQS
    try:
        sqs = boto3.client(
            'sqs',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            endpoint_url=os.getenv('SQS_ENDPOINT') or None,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID') if os.getenv('SQS_ENDPOINT') else None,
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY') if os.getenv('SQS_ENDPOINT') else None,
        )
        queue_name = os.getenv('SQS_QUEUE_NAME', 'jobs-queue')
        
        # Obtener URL de la cola
        queue_url_response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = queue_url_response['QueueUrl']
        
        # Obtener atributos básicos de la cola
        attrs = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
        )
        
        checks["checks"]["sqs"] = {
            "status": "healthy",
            "queue": queue_name,
            "messages_available": attrs['Attributes'].get('ApproximateNumberOfMessages', '0'),
            "messages_in_flight": attrs['Attributes'].get('ApproximateNumberOfMessagesNotVisible', '0')
        }
    except ClientError as e:
        all_healthy = False
        checks["checks"]["sqs"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    except Exception as e:
        all_healthy = False
        checks["checks"]["sqs"] = {
            "status": "unhealthy",
            "error": f"Unexpected error: {str(e)}"
        }
    
    # Determinar estado final
    if not all_healthy:
        checks["status"] = "degraded"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=checks
        )
    
    return checks

