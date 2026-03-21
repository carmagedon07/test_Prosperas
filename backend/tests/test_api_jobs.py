"""
Tests unitarios para la API de jobs (POST /jobs endpoint).
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from uuid import uuid4
import json


@pytest.mark.unit
def test_create_job_success(test_client, sample_job_data):
    """Test: Crear un job exitosamente con autenticación."""
    with patch('app.api.dependencies.get_current_user') as mock_user, \
         patch('app.api.routes.jobs.create_job_use_case') as mock_use_case, \
         patch('boto3.client') as mock_boto:
        
        # Mock usuario autenticado
        mock_user.return_value = {
            'id': 'testuser',
            'username': 'testuser',
            'role': 'user'
        }
        
        # Mock use case execute
        job_id = uuid4()
        mock_job = MagicMock()
        mock_job.job_id = job_id
        mock_job.user_id = 'testuser'
        mock_job.status = 'PENDING'
        mock_job.report_type = sample_job_data['report_type']
        mock_job.date_range = sample_job_data['date_range']
        mock_job.format = sample_job_data['format']
        mock_job.created_at = '2024-01-01T00:00:00'
        mock_job.updated_at = '2024-01-01T00:00:00'
        
        mock_use_case.execute.return_value = mock_job
        
        # Mock SQS client
        mock_sqs = MagicMock()
        mock_boto.return_value = mock_sqs
        mock_sqs.send_message.return_value = {'MessageId': 'test-msg'}
        
        # Hacer request con token dummy (será mockeado)
        response = test_client.post(
            "/api/jobs",
            json=sample_job_data,
            headers={"Authorization": "Bearer dummy-token"}
        )
        
        # Verificar respuesta
        assert response.status_code == 201


@pytest.mark.unit
def test_create_job_unauthorized(test_client, sample_job_data):
    """Test: Crear job sin token JWT debe retornar 401."""
    response = test_client.post("/api/jobs", json=sample_job_data)
    assert response.status_code == 401


@pytest.mark.unit
def test_create_job_invalid_data(test_client):
    """Test: Crear job con datos inválidos debe retornar 422."""
    with patch('app.api.dependencies.get_current_user') as mock_user:
        # Mock usuario autenticado
        mock_user.return_value = {'user_id': 'testuser', 'role': 'user'}
        
        invalid_data = {
            "report_type": "",  # Campo vacío
            "format": "INVALID_FORMAT"
        }
        
        response = test_client.post(
            "/api/jobs",
            json=invalid_data,
            headers={"Authorization": "Bearer dummy-token"}
        )
        
        assert response.status_code == 422


@pytest.mark.unit
def test_get_jobs_list(test_client):
    """Test: Obtener lista de jobs paginada."""
    with patch('app.api.dependencies.get_current_user') as mock_user, \
         patch('app.api.routes.jobs.list_jobs_use_case') as mock_use_case:
        
        # Mock usuario
        mock_user.return_value = {'id': 'testuser', 'role': 'user'}
        
        # Mock use case response
        mock_use_case.execute.return_value = {
            'items': [
                {
                    'job_id': str(uuid4()),
                    'status': 'COMPLETED',
                    'report_type': 'financial'
                }
            ],
            'pagination': {
                'page': 1,
                'page_size': 10,
                'total_items': 1
            }
        }
        
        response = test_client.get(
            "/api/jobs?page=1&page_size=10",
            headers={"Authorization": "Bearer dummy-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'pagination' in data


@pytest.mark.unit
def test_get_job_by_id(test_client, sample_job_id):
    """Test: Obtener un job por ID."""
    with patch('app.api.dependencies.get_current_user') as mock_user, \
         patch('app.api.routes.jobs.get_job_use_case') as mock_use_case:
        
        # Mock usuario
        mock_user.return_value = {'id': 'testuser', 'role': 'user'}
        
        # Mock use case get
        mock_job = MagicMock()
        mock_job.job_id = sample_job_id
        mock_job.status = 'PENDING'
        mock_job.report_type = 'financial'
        mock_use_case.execute.return_value = mock_job
        
        response = test_client.get(
            f"/api/jobs/{sample_job_id}",
            headers={"Authorization": "Bearer dummy-token"}
        )
        
        assert response.status_code == 200


@pytest.mark.unit
def test_get_job_not_found(test_client):
    """Test: Obtener job que no existe debe retornar 404."""
    with patch('app.api.dependencies.get_current_user') as mock_user, \
         patch('app.api.routes.jobs.get_job_use_case') as mock_use_case:
        
        # Mock usuario
        mock_user.return_value = {'id': 'testuser', 'role': 'user'}
        
        # Mock uso case retorna None
        mock_use_case.execute.return_value = None
        
        fake_id = str(uuid4())
        response = test_client.get(
            f"/api/jobs/{fake_id}",
            headers={"Authorization": "Bearer dummy-token"}
        )
        
        assert response.status_code == 404


@pytest.mark.unit
def test_delete_all_jobs_admin(test_client):
    """Test: Admin puede eliminar todos los jobs."""
    with patch('app.api.dependencies.get_current_user') as mock_user, \
         patch('app.api.dependencies.require_admin') as mock_admin, \
         patch('app.api.routes.jobs.delete_all_jobs_use_case') as mock_use_case:
        
        # Mock usuario admin
        mock_user.return_value = {
            'id': 'admin',
            'role': 'admin'
        }
        mock_admin.return_value = None  # No lanza excepción
        
        # Mock delete_all
        mock_use_case.execute.return_value = {
            'deleted_count': 5,
            'message': '5 jobs eliminados'
        }
        
        response = test_client.delete(
            "/api/jobs",
            headers={"Authorization": "Bearer dummy-token"}
        )
        
        assert response.status_code == 200

