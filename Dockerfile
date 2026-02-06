# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only dependency files first for efficient caching
COPY pyproject.toml poetry.lock* /app/

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Poetry (if you use it) and dependencies
RUN pip install --upgrade pip
RUN pip install poetry

# Install project dependencies
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Copy the rest of your app code
COPY . /app/

# Expose port (if your app runs a server; adjust if needed)
EXPOSE 8000

# Default command — adjust based on your app
CMD ["python", "main.py"]
