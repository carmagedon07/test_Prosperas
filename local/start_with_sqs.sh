#!/bin/sh
# Script para iniciar LocalStack, esperar la cola SQS y luego lanzar el resto de servicios

set -e

QUEUE_NAME="test-queue"

# 1. Iniciar solo LocalStack

echo "Iniciando LocalStack..."
docker-compose up -d localstack

# 2. Esperar a que LocalStack esté listo y crear la cola si no existe
until docker-compose exec localstack awslocal sqs list-queues; do
  echo "Esperando a que LocalStack esté listo..."
  sleep 2
done

echo "Verificando existencia de la cola SQS: $QUEUE_NAME"
if ! docker-compose exec localstack awslocal sqs get-queue-url --queue-name "$QUEUE_NAME" 2>/dev/null; then
  echo "Creando cola SQS: $QUEUE_NAME"
  docker-compose exec localstack awslocal sqs create-queue --queue-name "$QUEUE_NAME"
else
  echo "La cola SQS $QUEUE_NAME ya existe."
fi

# 3. Levantar el resto de servicios

echo "Levantando backend, worker y frontend..."
docker-compose up -d backend worker frontend

echo "¡Todo listo!"
