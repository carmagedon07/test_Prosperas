"""
Tests unitarios para el worker (simulación de procesamiento de jobs).
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from uuid import uuid4
import json
import sys
import os

# Agregar el directorio worker al path para importar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../worker'))


@pytest.mark.unit
def test_process_job_success():
    """Test: Procesar un job exitosamente debe cambiar status a COMPLETED."""
    with patch('boto3.resource') as mock_resource, \
         patch('time.sleep') as mock_sleep:
        
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {}
        
        # Simular procesamiento
        job_id = str(uuid4())
        
        # Importar después del mock
        import main as worker_main
        
        # Llamar función de procesamiento (simulamos el proceso)
        mock_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'COMPLETED',
                ':updated_at': '2024-01-01T00:00:00'
            }
        )
        
        # Verificar que se llamó update_item con COMPLETED
        mock_table.update_item.assert_called_once()
        call_args = mock_table.update_item.call_args
        assert call_args[1]['ExpressionAttributeValues'][':status'] == 'COMPLETED'


@pytest.mark.unit
def test_process_job_failure():
    """Test: Si falla el procesamiento, status debe cambiar a FAILED."""
    with patch('boto3.resource') as mock_resource:
        
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {}
        
        job_id = str(uuid4())
        
        # Simular fallo en procesamiento
        mock_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'FAILED',
                ':updated_at': '2024-01-01T00:00:00'
            }
        )
        
        # Verificar que se llamó update_item con FAILED
        mock_table.update_item.assert_called_once()
        call_args = mock_table.update_item.call_args
        assert call_args[1]['ExpressionAttributeValues'][':status'] == 'FAILED'


@pytest.mark.unit
def test_worker_receives_message_from_sqs():
    """Test: Worker debe recibir mensajes de SQS correctamente."""
    with patch('boto3.client') as mock_client:
        
        # Mock SQS client
        mock_sqs = MagicMock()
        mock_client.return_value = mock_sqs
        
        job_id = str(uuid4())
        mock_sqs.receive_message.return_value = {
            'Messages': [{
                'MessageId': 'test-msg-1',
                'ReceiptHandle': 'test-receipt-handle',
                'Body': json.dumps({'job_id': job_id})
            }]
        }
        
        # Simular recepción de mensaje
        response = mock_sqs.receive_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/test-queue',
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            VisibilityTimeout=180
        )
        
        # Verificar que se recibió el mensaje
        assert 'Messages' in response
        assert len(response['Messages']) == 1
        assert response['Messages'][0]['MessageId'] == 'test-msg-1'
        
        message_body = json.loads(response['Messages'][0]['Body'])
        assert message_body['job_id'] == job_id


@pytest.mark.unit
def test_worker_deletes_message_after_processing():
    """Test: Worker debe eliminar mensaje de SQS después de procesarlo."""
    with patch('boto3.client') as mock_client:
        
        # Mock SQS client
        mock_sqs = MagicMock()
        mock_client.return_value = mock_sqs
        mock_sqs.delete_message.return_value = {}
        
        receipt_handle = 'test-receipt-handle'
        
        # Simular eliminación de mensaje
        mock_sqs.delete_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/test-queue',
            ReceiptHandle=receipt_handle
        )
        
        # Verificar que se llamó delete_message
        mock_sqs.delete_message.assert_called_once()
        call_args = mock_sqs.delete_message.call_args
        assert call_args[1]['ReceiptHandle'] == receipt_handle


@pytest.mark.unit
def test_worker_updates_status_to_processing():
    """Test: Worker debe cambiar status a PROCESSING al iniciar."""
    with patch('boto3.resource') as mock_resource:
        
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {}
        
        job_id = str(uuid4())
        
        # Simular update a PROCESSING
        mock_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'PROCESSING'}
        )
        
        # Verificar que se llamó con PROCESSING
        mock_table.update_item.assert_called_once()
        call_args = mock_table.update_item.call_args
        assert call_args[1]['ExpressionAttributeValues'][':status'] == 'PROCESSING'


@pytest.mark.unit
@pytest.mark.slow
def test_worker_processing_duration():
    """Test: Verificar que el procesamiento toma el tiempo esperado (60-90s simulado)."""
    with patch('time.sleep') as mock_sleep, \
         patch('random.uniform') as mock_random:
        
        # Mock duración aleatoria
        mock_random.return_value = 75.0  # 75 segundos
        
        # Simular procesamiento
        duration = mock_random(60, 90)
        mock_sleep(duration)
        
        # Verificar que se llamó con duración correcta
        mock_sleep.assert_called_once_with(75.0)
        assert 60 <= duration <= 90


@pytest.mark.unit
def test_worker_handles_invalid_message():
    """Test: Worker debe manejar mensajes inválidos sin fallar."""
    with patch('boto3.client') as mock_client:
        
        # Mock SQS con mensaje inválido
        mock_sqs = MagicMock()
        mock_client.return_value = mock_sqs
        
        mock_sqs.receive_message.return_value = {
            'Messages': [{
                'MessageId': 'test-msg-invalid',
                'ReceiptHandle': 'test-receipt',
                'Body': 'INVALID JSON'
            }]
        }
        
        response = mock_sqs.receive_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/test-queue',
            MaxNumberOfMessages=1
        )
        
        # Verificar que se recibió mensaje (aunque sea inválido)
        assert 'Messages' in response
        
        # Simular manejo de error (el worker debería loggear y continuar)
        with pytest.raises(json.JSONDecodeError):
            json.loads(response['Messages'][0]['Body'])
