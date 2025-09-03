# syntax=docker/dockerfile:1
FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --python=3.12 || true

COPY src ./src

CMD ["uv", "run", "python", "src/auto_task_manager/main.py"]
