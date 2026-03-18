from fastapi import FastAPI
from .api.routes import jobs
from .api.routes import auth
from .api.exception_handlers import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from .infrastructure.db.session import Base, engine
from .worker.fake_worker import start_fake_worker
from .application.use_cases.create_job import CreateJobUseCase
from .infrastructure.repositories.job_repository_sqlalchemy import JobRepositorySQLAlchemy

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Registrar rutas
app.include_router(auth.router)
app.include_router(jobs.router)

# Registrar handlers globales
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Hook para lanzar el fake worker tras crear un job
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from uuid import UUID

# Monkey patch del endpoint POST /jobs para lanzar el worker
for route in app.routes:
    if isinstance(route, APIRoute) and route.path == "/jobs" and "POST" in route.methods:
        original_endpoint = route.endpoint
        async def endpoint_with_worker(*args, **kwargs):
            response = await original_endpoint(*args, **kwargs)
            job_id = response.job_id if hasattr(response, "job_id") else response["job_id"]
            start_fake_worker(job_id)
            return response
        route.endpoint = endpoint_with_worker
