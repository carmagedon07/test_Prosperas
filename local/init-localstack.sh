#!/bin/sh
# ============================================================
#  Inicializa los recursos AWS en LocalStack:
#   - SQS: jobs-queue (con DLQ)
#   - DynamoDB: tabla jobs (con GSI por user_id)
#   - DynamoDB: tabla users
# ============================================================
set -e

ENDPOINT="http://localstack:4566"
REGION="us-east-1"
ACCOUNT="000000000000"

echo "========================================"
echo " Inicializando recursos AWS en LocalStack"
echo "========================================"

# ── Dead Letter Queue ─────────────────────────────────────
echo "--> Creando DLQ: jobs-dlq"
aws --endpoint-url=$ENDPOINT sqs create-queue \
  --queue-name jobs-dlq \
  --region $REGION

DLQ_ARN="arn:aws:sqs:${REGION}:${ACCOUNT}:jobs-dlq"

# ── Cola principal con redrive hacia DLQ ──────────────────
echo "--> Creando cola principal: jobs-queue (maxReceiveCount=3)"
aws --endpoint-url=$ENDPOINT sqs create-queue \
  --queue-name jobs-queue \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"${DLQ_ARN}\\\",\\\"maxReceiveCount\\\":\\\"3\\\"}\"}" \
  --region $REGION

# ── Tabla DynamoDB: jobs ──────────────────────────────────
echo "--> Creando tabla DynamoDB: jobs"
aws --endpoint-url=$ENDPOINT dynamodb create-table \
  --table-name jobs \
  --attribute-definitions \
    AttributeName=job_id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=job_id,KeyType=HASH \
  --global-secondary-indexes \
    '[{"IndexName":"UserIdIndex","KeySchema":[{"AttributeName":"user_id","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"},"ProvisionedThroughput":{"ReadCapacityUnits":5,"WriteCapacityUnits":5}}]' \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region $REGION

# ── Tabla DynamoDB: users ─────────────────────────────────
echo "--> Creando tabla DynamoDB: users"
aws --endpoint-url=$ENDPOINT dynamodb create-table \
  --table-name users \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region $REGION

echo "========================================"
echo " Inicializacion completada exitosamente"
echo "========================================"
