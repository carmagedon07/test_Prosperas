import os
import boto3

# Cargar variables de entorno
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL", "http://localhost:4566/000000000000/test-queue")

# Crear cliente SQS apuntando a LocalStack
sqs = boto3.client(
    "sqs",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url="http://localstack:4566"  # Cambia a None en producción
)

def send_test_message():
    response = sqs.send_message(
        QueueUrl=AWS_SQS_QUEUE_URL,
        MessageBody="Mensaje de prueba desde backend"
    )
    return response

if __name__ == "__main__":
    print(send_test_message())
