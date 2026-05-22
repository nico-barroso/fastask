FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

LABEL org.opencontainers.image.source="https://github.com/nico-barroso/fastask"
LABEL org.opencontainers.image.description="FastTask — Task and list management REST API with soft delete, pagination and UUID support. Built with FastAPI and Pydantic v2."
LABEL org.opencontainers.image.authors="Nico Barroso"
LABEL org.opencontainers.image.version="1.1.1"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

