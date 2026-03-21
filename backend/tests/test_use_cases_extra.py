"""
Tests unitarios adicionales para use_cases (list_jobs, delete_all_jobs).
"""
import pytest
from unittest.mock import Mock
from app.application.use_cases.list_jobs import ListJobsUseCase
from app.application.use_cases.delete_all_jobs import DeleteAllJobsUseCase
from uuid import uuid4


@pytest.mark.unit
def test_list_jobs_empty():
    """Test: Listar jobs cuando no hay ninguno."""
    # Mock repository que retorna lista vacía
    mock_repo = Mock()
    mock_repo.list.return_value = {
        'items': [],
        'pagination': {
            'page': 1,
            'page_size': 10,
            'total_items': 0
        }
    }
    
    use_case = ListJobsUseCase(mock_repo)
    result = use_case.execute(user_id="user-1", page=1, page_size=10)
    
    assert result['items'] == []
    assert result['pagination']['total_items'] == 0


@pytest.mark.unit
def test_list_jobs_with_results():
    """Test: Listar jobs con resultados."""
    job1_id = str(uuid4())
    job2_id = str(uuid4())
    
    # Mock repository con 2 jobs
    mock_repo = Mock()
    mock_repo.list.return_value = {
        'items': [
            {'job_id': job1_id, 'status': 'COMPLETED'},
            {'job_id': job2_id, 'status': 'PENDING'}
        ],
        'pagination': {
            'page': 1,
            'page_size': 10,
            'total_items': 2
        }
    }
    
    use_case = ListJobsUseCase(mock_repo)
    result = use_case.execute(user_id="user-1", page=1, page_size=10)
    
    assert len(result['items']) == 2
    assert result['pagination']['total_items'] == 2


@pytest.mark.unit
def test_delete_all_jobs():
    """Test: Eliminar todos los jobs de un usuario."""
    # Mock repository
    mock_repo = Mock()
    mock_repo.delete_all.return_value = {
        'deleted_count': 3,
        'message': '3 jobs eliminados'
    }
    
    use_case = DeleteAllJobsUseCase(mock_repo)
    result = use_case.execute(user_id="user-1")
    
    assert result['deleted_count'] == 3
    assert 'eliminados' in result['message']


@pytest.mark.unit
def test_delete_all_jobs_zero():
    """Test: Eliminar jobs cuando no hay ninguno."""
    # Mock repository que retorna 0 eliminados
    mock_repo = Mock()
    mock_repo.delete_all.return_value = {
        'deleted_count': 0,
        'message': '0 jobs eliminados'
    }
    
    use_case = DeleteAllJobsUseCase(mock_repo)
    result = use_case.execute(user_id="user-1")
    
    assert result['deleted_count'] == 0
