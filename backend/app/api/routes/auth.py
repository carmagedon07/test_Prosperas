from fastapi import APIRouter
from pydantic import BaseModel
from ...core.security import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    user_id: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    # Validación simple de credenciales
    if request.user_id == "superadmin":
        if request.password != "superpassword":
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Invalid credentials")
    # Para otros usuarios, puedes aceptar cualquier password (o agregar más reglas)
    token = create_access_token(user_id=request.user_id)
    return TokenResponse(access_token=token)
