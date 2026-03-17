# CHF Digital Twin Backend

This repository contains a FastAPI backend for a chronic heart failure digital twin system, including simulation APIs and a static frontend.

## Docker deployment (recommended)

### Prerequisites

- Docker Desktop (or Docker Engine) must be installed and running.
- Ensure Docker can access the host filesystem where this project exists.
- Put your Fitbit OAuth settings in a `.env` file at the repo root (example below).

Example `.env`:

```env
FITBIT_CLIENT_ID=your_id_here
FITBIT_CLIENT_SECRET=your_secret_here
FITBIT_REDIRECT_URI=http://localhost:8000/auth/fitbit/callback
```

### 1) Build and start the container

```bash
# Build the image and start the service
docker compose up --build -d
```

### 2) Verify it is running

- API: http://localhost:8000/api/test
- Frontend: http://localhost:8000/

### 3) Stop / remove containers

```bash
docker compose down
```

## Notes

- The backend uses `chf_digital_twin.db` as its default SQLite database. The compose setup mounts it from the host for persistence.
- Fitbit OAuth configuration is loaded from environment variables via `.env`.
