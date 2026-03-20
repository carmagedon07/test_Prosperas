# localstack-init/01-create-queues.sh
#!/bin/bash
echo "Creando colas SQS..."

awslocal sqs create-queue --queue-name test-queue

echo "Colas creadas:"
awslocal sqs list-queues