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


app = FastAPI()

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
app.include_router(auth.router)
app.include_router(jobs.router)

# Registrar handlers globales
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

