FROM python:3.11-slim

# Build context is the repo root (d:\test_prospera)
# docker-compose sets:  context: ..  dockerfile: worker/Dockerfile

WORKDIR /app

# Install dependencies from backend
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend shared modules (domain, use cases, infrastructure)
COPY backend/app /app/backend/app

# Copy worker code
COPY worker/main.py /app/worker/main.py

# Python path: worker can import from backend
ENV PYTHONPATH=/app/worker:/app/backend

CMD ["python", "/app/worker/main.py"]
