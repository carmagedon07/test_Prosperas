
import boto3
import os
import json

SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "test-queue")
SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://localstack:4566")
QUEUE_URL = f"{SQS_ENDPOINT}/000000000000/{SQS_QUEUE_NAME}"

sqs = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT,
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
)

def send_job_message(job_id: str):
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({"job_id": job_id})
    )
