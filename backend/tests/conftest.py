"""
Fixtures compartidos para tests de pytest.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime


@pytest.fixture
def test_client():
    """Cliente de prueba para la API FastAPI."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_jwt_token():
    """Token JWT mock para autenticación en tests."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6OTk5OTk5OTk5OX0.test"


@pytest.fixture
def mock_dynamodb_table():
    """Mock de tabla DynamoDB."""
    table = MagicMock()
    table.put_item = Mock(return_value={})
    table.get_item = Mock(return_value={
        'Item': {
            'job_id': str(uuid4()),
            'user_id': 'testuser',
            'status': 'PENDING',
            'report_type': 'financial',
            'date_range': '2024-01',
            'format': 'PDF',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
        }
    })
    table.query = Mock(return_value={'Items': []})
    table.scan = Mock(return_value={'Items': []})
    table.update_item = Mock(return_value={})
    table.delete_item = Mock(return_value={})
    return table


@pytest.fixture
def mock_sqs_client():
    """Mock de cliente SQS."""
    sqs = MagicMock()
    sqs.get_queue_url = Mock(return_value={
        'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'
    })
    sqs.send_message = Mock(return_value={
        'MessageId': 'test-message-id',
        'MD5OfMessageBody': 'test-md5'
    })
    sqs.receive_message = Mock(return_value={
        'Messages': [{
            'MessageId': 'test-msg-1',
            'ReceiptHandle': 'test-receipt',
            'Body': '{"job_id": "test-job-123"}'
        }]
    })
    sqs.delete_message = Mock(return_value={})
    return sqs


@pytest.fixture
def sample_job_data():
    """Datos de ejemplo para crear un job."""
    return {
        "report_type": "financial",
        "date_range": "2024-01",
        "format": "PDF"
    }


@pytest.fixture
def sample_job_id():
    """UUID de ejemplo para un job."""
    return uuid4()
