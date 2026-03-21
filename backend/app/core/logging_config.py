"""
Configuración de logging estructurado (JSON) para producción.
Permite logs legibles en desarrollo (text) y logs parseables en producción (json).
"""
import logging
import json
import sys
import os
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Formatter que convierte logs a formato JSON estructurado.
    Incluye timestamp ISO8601, level, message, y campos extras.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Agregar información de la fuente del log
        if record.filename:
            log_data["file"] = record.filename
        if record.lineno:
            log_data["line"] = record.lineno
        if record.funcName:
            log_data["function"] = record.funcName
        
        # Agregar exception info si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Agregar campos extra del record
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'lineno', 'module', 'msecs', 'message', 'exc_info',
                'exc_text', 'stack_info', 'pathname', 'process', 'processName',
                'relativeCreated', 'thread', 'threadName', 'taskName', 'levelno'
            ]:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    log_level: str = None,
    log_format: str = None
):
    """
    Configura el sistema de logging de la aplicación.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   Default: INFO (producción) o DEBUG (desarrollo)
        log_format: Formato de logs: 'json' (estructurado) o 'text' (legible)
                    Default: json (producción) o text (desarrollo)
    """
    # Valores por defecto desde variables de entorno
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    if log_format is None:
        log_format = os.getenv('LOG_FORMAT', 'text').lower()
    
    # Validar log level
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configurar handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Aplicar formatter según el formato solicitado
    if log_format == 'json':
        handler.setFormatter(JSONFormatter())
    else:
        # Formato text legible para desarrollo
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remover handlers existentes para evitar duplicados
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Silenciar logs verbose de librerías externas
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    
    return root_logger


# Logger para uso general en la aplicación
logger = logging.getLogger(__name__)
