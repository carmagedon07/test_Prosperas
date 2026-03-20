from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ...core.security import create_access_token
from ...infrastructure.repositories.user_repository_dynamodb import UserRepositoryDynamoDB

router = APIRouter()

class LoginRequest(BaseModel):
    user_id: str
    password: str

class RegisterRequest(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class RegisterResponse(BaseModel):
    user_id: str
    role: str
    message: str = "Usuario creado exitosamente"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Initialize user repository
user_repository = UserRepositoryDynamoDB()

@router.post("/auth/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest):
    """
    Register a new user. Open endpoint — no authentication required.
    Role is always 'user'.
    """
    if user_repository.exists(request.user_id):
        raise HTTPException(status_code=409, detail="El usuario ya existe")
    user = user_repository.create_user(request.user_id, request.password, role='user')
    return RegisterResponse(user_id=user['user_id'], role=user['role'])


@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Authenticate user against DynamoDB users table
    """
    user = user_repository.authenticate(request.user_id, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user_id=user['user_id'])
    return TokenResponse(access_token=token)
