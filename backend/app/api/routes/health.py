from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check():
    """Health check endpoint — usado por el ALB de AWS para verificar que el backend está vivo."""
    return {"status": "ok", "service": "backend"}
