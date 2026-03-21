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
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "test-queue")
# None → usa endpoints reales de AWS; valor → apunta a localstack (desarrollo local)
SQS_ENDPOINT = os.getenv("SQS_ENDPOINT") or None

# Para LocalStack: usa credenciales test
# Para AWS: boto3 usa automáticamente el ECS Task Role
sqs_params = {'region_name': AWS_REGION}

# Solo para LocalStack (desarrollo local)
if SQS_ENDPOINT:
    sqs_params['endpoint_url'] = SQS_ENDPOINT
    sqs_params['aws_access_key_id'] = 'test'
    sqs_params['aws_secret_access_key'] = 'test'

sqs = boto3.client("sqs", **sqs_params)


def resolve_queue_url(sqs_client, queue_name: str) -> str:
    """Resuelve la URL de la cola. Funciona con localstack y AWS real."""
    explicit = os.getenv("SQS_QUEUE_URL")
    if explicit:
        return explicit
    return sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]


def wait_for_queue(sqs_client, queue_name: str, timeout: int = 60) -> str:
    """Espera a que la cola esté disponible y retorna su URL."""
    import botocore
    start = time.time()
    while True:
        try:
            url = resolve_queue_url(sqs_client, queue_name)
            sqs_client.get_queue_attributes(QueueUrl=url, AttributeNames=["QueueArn"])
            print(f"[WORKER] Cola SQS disponible: {url}")
            return url
        except botocore.exceptions.ClientError:
            if time.time() - start > timeout:
                raise RuntimeError(f"[WORKER] Timeout esperando la cola '{queue_name}'")
            print("[WORKER] Esperando a que la cola SQS esté disponible...")
            time.sleep(2)


def process_job(job_id: str, receipt_handle: str, queue_url: str):
    """Procesa un job y elimina el mensaje de SQS al terminar (éxito o fallo)."""
    instance_id = os.getenv("WORKER_INSTANCE_ID", "default")
    job_repository = JobRepositoryDynamoDB()
    update_status_use_case = UpdateJobStatusUseCase(job_repository)
    try:
        update_status_use_case.execute(UUID(job_id), JobStatus.PROCESSING)
        duration = random.uniform(5, 30)
        print(f"[{instance_id}] Procesando job_id: {job_id} (duración: {duration:.1f}s)")
        time.sleep(duration)
        # Aleatoriamente COMPLETED o FAILED
        if random.choice([True, False]):
            result_url = f"https://dummy.result/{job_id}"
            update_status_use_case.execute(UUID(job_id), JobStatus.COMPLETED, result_url=result_url)
            print(f"[{instance_id}] job_id: {job_id} → COMPLETED")
        else:
            update_status_use_case.execute(UUID(job_id), JobStatus.FAILED, error_msg="Error simulado")
            print(f"[{instance_id}] job_id: {job_id} → FAILED")
    except Exception as e:
        print(f"[{instance_id}] Error procesando job {job_id}: {e}")
        try:
            update_status_use_case.execute(UUID(job_id), JobStatus.FAILED, error_msg=str(e))
        except Exception:
            pass
    finally:
        # Elimina el mensaje siempre para evitar reprocesamiento
        try:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        except Exception as e:
            print(f"[{instance_id}] Error eliminando mensaje de SQS: {e}")


def worker_loop(queue_url: str):
    instance_id = os.getenv("WORKER_INSTANCE_ID", "default")
    print(f"[{instance_id}] SQS Worker iniciado. Escuchando: {queue_url}")
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10,
                VisibilityTimeout=120,
            )
        except Exception as e:
            print(f"[{instance_id}] Error recibiendo mensajes: {e}")
            time.sleep(5)
            continue

        messages = response.get("Messages", [])
        for msg in messages:
            try:
                body = msg["Body"]
                try:
                    data = json.loads(body)
                    job_id = data["job_id"]
                except Exception:
                    job_id = body

                # Disparar thread y NO esperar (no t.join())
                # El mensaje se elimina dentro de process_job al finalizar
                t = threading.Thread(
                    target=process_job,
                    args=(job_id, msg["ReceiptHandle"], queue_url),
                    daemon=True,
                )
                t.start()

            except Exception as e:
                print(f"[{instance_id}] Error despachando mensaje: {e}")


if __name__ == "__main__":
    queue_url = wait_for_queue(sqs, SQS_QUEUE_NAME)
    worker_loop(queue_url)
