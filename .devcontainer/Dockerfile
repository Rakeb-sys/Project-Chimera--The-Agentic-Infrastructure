# Reuse the main Dockerfile — this just references it
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi
