# CHF Digital Twin Backend

This repository contains a FastAPI backend for a chronic heart failure digital twin system, including simulation APIs and a static frontend.

## Docker deployment (recommended)

### Prerequisites

- Docker Desktop (or Docker Engine) must be installed and running.
- Ensure Docker can access the host filesystem where this project exists.
- Put your Fitbit OAuth settings in a `.env` file at the repo root (example below). You can start from the provided `.env.example`.

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

## Deploy to Render (Docker)

Render can build and run this repository directly from the `Dockerfile`. A `render.yaml` is included in this repo so Render can auto-detect settings when you connect the repo.

1. Create a new **Web Service** on Render.
2. Connect your GitHub repo and select the `main` branch.
3. For **Environment**, choose **Docker**.
4. (Optional) If Render asks for a **Build Command**, you can leave it blank; Render will use the `Dockerfile`.
5. Configure environment variables (Render supports a UI for this):
   - `FITBIT_CLIENT_ID`, `FITBIT_CLIENT_SECRET`, `FITBIT_REDIRECT_URI` (if using Fitbit integration)
   - Any other custom vars your deployment needs.

> ✅ Render sets the `PORT` environment variable for you. This project reads `$PORT` in `Dockerfile` and `run.py`, so it works locally (defaulting to 8000) and on Render.

6. Deploy and then open the service URL. Your API should be reachable at:

```
https://<your-render-service>.onrender.com/api/test
```

## Notes

- The backend uses `chf_digital_twin.db` as its default SQLite database. The compose setup mounts it from the host for persistence.
- Fitbit OAuth configuration is loaded from environment variables via `.env`.
