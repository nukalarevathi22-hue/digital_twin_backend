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

# Expose the port used by FastAPI (default)
EXPOSE 8000

# Use PORT env var so this works locally (default 8000) and on Render (sets $PORT)
ENV PORT=8000

# Default command - run the app using Uvicorn
# Render sets $PORT automatically; we fall back to the default when running locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
