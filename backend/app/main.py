from fastapi import FastAPI
from .api.routes import jobs
from .api.routes import auth
from .api.routes import health
from .api.exception_handlers import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .core.logging_config import setup_logging
import logging
import os

# Configurar logging estructurado al inicio de la aplicación
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Prospera Jobs API", version="1.0.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a los orígenes permitidos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")

# Registrar handlers globales
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.on_event("startup")
async def startup_event():
    """Log de información de configuración al iniciar la aplicación."""
    logger.info(
        "Prospera Jobs API iniciada",
        extra={
            "environment": os.getenv("ENVIRONMENT", "development"),
            "aws_region": os.getenv("AWS_REGION", "us-east-1"),
            "dynamodb_table": os.getenv("DYNAMODB_TABLE_NAME", "jobs"),
            "sqs_queue": os.getenv("SQS_QUEUE_NAME", "jobs-queue"),
            "log_format": os.getenv("LOG_FORMAT", "text"),
        }
    )

