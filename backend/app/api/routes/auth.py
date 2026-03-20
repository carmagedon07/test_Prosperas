from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...core.security import create_access_token
from ...infrastructure.repositories.user_repository_dynamodb import UserRepositoryDynamoDB

router = APIRouter()

class LoginRequest(BaseModel):
    user_id: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Initialize user repository
user_repository = UserRepositoryDynamoDB()

@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Authenticate user against DynamoDB users table
    """
    # Authenticate user
    user = user_repository.authenticate(request.user_id, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    token = create_access_token(user_id=user['user_id'])
    return TokenResponse(access_token=token)
