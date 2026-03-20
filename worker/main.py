import os
import sys
import time
import random
import threading
import boto3
import json
from uuid import UUID

# Add backend to path to share code
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.application.use_cases.update_job_status import UpdateJobStatusUseCase
from app.domain.enums.job_status import JobStatus
from app.infrastructure.repositories.job_repository_dynamodb import JobRepositoryDynamoDB

# AWS/SQS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "test-queue")
SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://localstack:4566")
AWS_SQS_QUEUE_URL = f"{SQS_ENDPOINT}/000000000000/{SQS_QUEUE_NAME}"

sqs = boto3.client(
    "sqs",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=SQS_ENDPOINT
)


def wait_for_queue(sqs_client, queue_url, timeout=60):
    import botocore
    import time
    start = time.time()
    while True:
        try:
            sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])
            print(f"[WORKER] Cola SQS disponible: {queue_url}")
            return
        except botocore.exceptions.ClientError as e:
            if time.time() - start > timeout:
                print(f"[WORKER] Timeout esperando la cola SQS: {queue_url}")
                raise
            print(f"[WORKER] Esperando a que la cola SQS esté disponible...")
            time.sleep(2)


def process_job(job_id: str):
    job_repository = JobRepositoryDynamoDB()
    update_status_use_case = UpdateJobStatusUseCase(job_repository)
    try:
        update_status_use_case.execute(UUID(job_id), JobStatus.PROCESSING)
        print(f"[WORKER] Procesando job_id: {job_id} (esperando 60s)")
        time.sleep(60)
        # Aleatoriamente COMPLETED o FAILED
        if random.choice([True, False]):
            result_url = f"https://dummy.result/{job_id}"
            update_status_use_case.execute(UUID(job_id), JobStatus.COMPLETED, result_url=result_url)
            print(f"[WORKER] job_id: {job_id} COMPLETED")
        else:
            update_status_use_case.execute(UUID(job_id), JobStatus.FAILED, error_msg="Error simulado")
            print(f"[WORKER] job_id: {job_id} FAILED")
    except Exception as e:
        print(f"[WORKER] Error procesando job {job_id}: {e}")
        try:
            update_status_use_case.execute(UUID(job_id), JobStatus.FAILED, error_msg=str(e))
        except:
            pass


def worker_loop():
    print("SQS Worker iniciado. Esperando mensajes...")
    while True:
        response = sqs.receive_message(
            QueueUrl=AWS_SQS_QUEUE_URL,
            MaxNumberOfMessages=2,  # Procesar hasta 2 mensajes a la vez
            WaitTimeSeconds=10
        )
        messages = response.get("Messages", [])
        threads = []
        for msg in messages:
            try:
                body = msg["Body"]
                # Si el body es JSON, extrae el job_id
                try:
                    data = json.loads(body)
                    job_id = data["job_id"]
                except Exception:
                    job_id = body
                t = threading.Thread(target=process_job, args=(job_id,))
                t.start()
                threads.append((t, msg["ReceiptHandle"]))
            except Exception as e:
                print(f"Error procesando mensaje: {e}")
        # Esperar a que terminen los threads y luego borrar los mensajes
        for t, receipt_handle in threads:
            t.join()
            try:
                sqs.delete_message(
                    QueueUrl=AWS_SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
            except Exception as e:
                print(f"Error eliminando mensaje: {e}")
        time.sleep(1)


if __name__ == "__main__":
    wait_for_queue(sqs, AWS_SQS_QUEUE_URL)
    worker_loop()
