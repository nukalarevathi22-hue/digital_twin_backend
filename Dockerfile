# Dockerfile for CHF Digital Twin Backend
# Build a lightweight container running FastAPI + Uvicorn

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for OpenCV, python-magic, etc.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        ca-certificates \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy application code
COPY . /app

# Create directories used at runtime
RUN mkdir -p /app/uploads /app/data

# Expose the port used by FastAPI
EXPOSE 10000

# Default command - run the app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
