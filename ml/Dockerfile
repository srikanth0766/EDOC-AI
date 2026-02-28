FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install only what the ML service needs (lightweight — no torch for heuristic MVP)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY smell_api.py .

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "smell_api:app", "--host", "0.0.0.0", "--port", "8001"]
