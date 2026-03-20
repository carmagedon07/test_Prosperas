FROM python:3.11-slim

WORKDIR /app

# Copy backend code to share domain, use cases, and infrastructure
COPY ../backend/app /app/backend/app

# Copy worker code
COPY . /app/worker

# Install dependencies
COPY ../backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Set Python path to include backend
ENV PYTHONPATH=/app/worker:/app/backend

CMD ["python", "/app/worker/main.py"]
