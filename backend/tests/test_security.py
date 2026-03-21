"""
Tests unitarios para el módulo de seguridad (JWT tokens).
"""
import pytest
from app.core.security import create_access_token, verify_token
from datetime import timedelta


@pytest.mark.unit
def test_create_access_token_user():
    """Test: Crear token JWT para usuario debe retornar string."""
    user_id = "testuser"
    token = create_access_token(user_id)
    
    # Verificar que el token es un string
    assert isinstance(token, str)
    # Verificar que tiene el formato JWT (3 partes separadas por .)
    assert len(token.split(".")) == 3


@pytest.mark.unit
def test_create_access_token_admin():
    """Test: Crear token para superadmin debe tener role=admin."""
    user_id = "superadmin"
    token = create_access_token(user_id)
    
    # Verificar y decodificar
    decoded = verify_token(token)
    
    # Verificar que el role es admin para superadmin
    assert decoded is not None
    assert decoded["id"] == "superadmin"
    assert decoded["role"] == "admin"


@pytest.mark.unit
def test_create_access_token_regular_user():
    """Test: Crear token para usuario regular debe tener role=user."""
    user_id = "regularuser"
    token = create_access_token(user_id)
    
    # Verificar y decodificar
    decoded = verify_token(token)
    
    # Verificar que el role es user
    assert decoded is not None
    assert decoded["id"] == "regularuser"
    assert decoded["role"] == "user"


@pytest.mark.unit
def test_create_access_token_with_custom_expiry():
    """Test: Crear token con tiempo de expiración personalizado."""
    user_id = "testuser"
    custom_expiry = timedelta(minutes=15)
    token = create_access_token(user_id, expires_delta=custom_expiry)
    
    # Verificar que el token es válido
    assert isinstance(token, str)
    
    # Decodificar y verificar
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded["id"] == "testuser"


@pytest.mark.unit
def test_verify_token_success():
    """Test: Verificar token válido debe retornar payload."""
    user_id = "user-123"
    token = create_access_token(user_id)
    
    # Verificar el token
    decoded = verify_token(token)
    
    # Verificar que el payload se decodificó correctamente
    assert decoded is not None
    assert decoded["id"] == "user-123"
    assert "role" in decoded


@pytest.mark.unit
def test_verify_token_invalid():
    """Test: Verificar token inválido debe retornar None."""
    invalid_token = "invalid.token.here"
    
    # Verificar token inválido
    decoded = verify_token(invalid_token)
    
    # Debe retornar None
    assert decoded is None


@pytest.mark.unit
def test_verify_token_missing_fields():
    """Test: Token sin campos requeridos debe retornar None."""
    from jose import jwt
    import os
    
    # Crear token sin el campo 'sub'
    payload = {"other_field": "value"}
    secret = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    malformed_token = jwt.encode(payload, secret, algorithm="HS256")
    
    # Verificar token malformado
    decoded = verify_token(malformed_token)
    
    # Debe retornar None porque falta 'sub'
    assert decoded is None


@pytest.mark.unit
def test_verify_token_expired():
    """Test: Verificar token expirado debe retornar None."""
    from jose import jwt
    import os
    from datetime import datetime, timedelta
    
    # Crear token con expiración de -1 segundo (ya expirado)
    payload = {
        "sub": "user-123",
        "role": "user",
        "exp": datetime.utcnow() - timedelta(seconds=1)  # Expirado hace 1 segundo
    }
    
    secret = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    expired_token = jwt.encode(payload, secret, algorithm="HS256")
    
    # Verificar token expirado
    decoded = verify_token(expired_token)
    
    # Debe retornar None
    assert decoded is None
