from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from ..core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

from typing import Dict

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    user = verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_admin(current_user: Dict[str, str] = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
