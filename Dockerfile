FROM python:3.11-slim
WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY models ./models
RUN pip install --no-cache-dir .

# Overridden per-service in docker-compose.yml.
CMD ["uvicorn", "pnwater.services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
