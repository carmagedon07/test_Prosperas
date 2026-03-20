"""
init_aws.py — Inicializa los recursos AWS en LocalStack:
  - SQS: jobs-dlq + jobs-queue (con redrive hacia DLQ)
  - DynamoDB: tabla jobs (PK=job_id, GSI=UserIdIndex/user_id)
  - DynamoDB: tabla users (PK=user_id)

Se ejecuta una vez al levantar el entorno local con docker compose.
"""
import boto3
import json
import sys

ENDPOINT = "http://localstack:4566"
REGION   = "us-east-1"
ACCOUNT  = "000000000000"

session = boto3.session.Session()

sqs = session.client(
    "sqs",
    endpoint_url=ENDPOINT,
    region_name=REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

ddb = session.client(
    "dynamodb",
    endpoint_url=ENDPOINT,
    region_name=REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

# ── SQS: Dead Letter Queue ─────────────────────────────────────────────
print("==> Creando DLQ: jobs-dlq")
dlq_resp = sqs.create_queue(QueueName="jobs-dlq")
dlq_url  = dlq_resp["QueueUrl"]
dlq_arn  = f"arn:aws:sqs:{REGION}:{ACCOUNT}:jobs-dlq"
print(f"    URL: {dlq_url}")

# ── SQS: cola principal ────────────────────────────────────────────────
print("==> Creando cola principal: jobs-queue")
q_resp = sqs.create_queue(
    QueueName="jobs-queue",
    Attributes={
        "RedrivePolicy": json.dumps({
            "deadLetterTargetArn": dlq_arn,
            "maxReceiveCount":     "3",
        }),
        "VisibilityTimeout": "120",
    },
)
print(f"    URL: {q_resp['QueueUrl']}")

# ── DynamoDB: tabla jobs ───────────────────────────────────────────────
print("==> Creando tabla DynamoDB: jobs")
try:
    ddb.create_table(
        TableName="jobs",
        AttributeDefinitions=[
            {"AttributeName": "job_id",  "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "job_id", "KeyType": "HASH"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "UserIdIndex",
                "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits":  5,
                    "WriteCapacityUnits": 5,
                },
            }
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    print("    Tabla 'jobs' creada.")
except ddb.exceptions.ResourceInUseException:
    print("    Tabla 'jobs' ya existe — saltando.")

# ── DynamoDB: tabla users ──────────────────────────────────────────────
print("==> Creando tabla DynamoDB: users")
try:
    ddb.create_table(
        TableName="users",
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    print("    Tabla 'users' creada.")
except ddb.exceptions.ResourceInUseException:
    print("    Tabla 'users' ya existe — saltando.")

print("==> Inicializacion completada exitosamente")
sys.exit(0)
