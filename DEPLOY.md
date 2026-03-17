# Deployment Guide: GitHub → Render

This guide will help you deploy your CHF Digital Twin Backend to **Render.com** (free tier) via GitHub.

---

## Step 1: Initialize Git & Push to GitHub

### 1.1 Configure Git (if not already done)
```powershell
cd "c:\Users\revat\Downloads\virtual\digital_twin_backend"
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 1.2 Stage and commit your files
```powershell
git add .
git commit -m "Initial commit: CHF Digital Twin Backend with Docker setup"
```

### 1.3 Create a GitHub repository
1. Go to https://github.com/new
2. Create repository named: `digital-twin-backend`
3. **Do NOT** initialize with README (you already have one)
4. Copy the repository URL (e.g., `https://github.com/YOUR_USERNAME/digital-twin-backend.git`)

### 1.4 Push to GitHub
```powershell
git remote add origin https://github.com/YOUR_USERNAME/digital-twin-backend.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Render.com

### 2.1 Create a Render account
1. Go to https://render.com/register
2. Sign up with GitHub (easiest option)
3. Verify your email

### 2.2 Create a new Web Service
1. Log in to Render Dashboard: https://dashboard.render.com
2. Click **"Create New +"** → **"Web Service"**
3. Select **"Build and deploy from a Git repository"**
4. Authorize Render to access your GitHub
5. Select your `digital-twin-backend` repository
6. Configure:
   - **Name:** `digital-twin-backend`
   - **Region:** `Oregon` (or closest to you)
   - **Branch:** `main`
   - **Runtime:** `Docker`
   - **Plan:** `Free`

### 2.3 Add environment variables
On the "Advanced" section, add these environment variables:
```
FITBIT_CLIENT_ID = your_fitbit_id
FITBIT_CLIENT_SECRET = your_fitbit_secret
FITBIT_REDIRECT_URI = https://digital-twin-backend-xxxx.onrender.com/auth/fitbit/callback
```

(Note: Replace the URL with your actual Render domain)

### 2.4 Deploy
Click **"Create Web Service"**

Render will:
1. Build your Docker image
2. Deploy the container
3. Assign you a public URL like: `https://digital-twin-backend-xxxx.onrender.com`

---

## Step 3: Verify Your Public Deployment

Once deployed, access:
- 🏠 **Frontend:** `https://digital-twin-backend-xxxx.onrender.com`
- 🔗 **API Test:** `https://digital-twin-backend-xxxx.onrender.com/api/test`
- 📚 **API Docs:** `https://digital-twin-backend-xxxx.onrender.com/docs`

---

## Troubleshooting

### Build fails
- Check the Render build logs
- Ensure all Docker dependencies in `Dockerfile` are correct

### App crashes after deploy
- View Render logs: Dashboard → your service → "Logs"
- Ensure env variables are set correctly
- Check that port 8000 is exposed in Dockerfile

### Rate limiting / Free tier limits
- Free tier apps sleep after 15 mins of inactivity
- They automatically restart when accessed again
- For persistent uptime, upgrade to paid tier

---

## Auto-deployment from GitHub
After this initial setup, any `git push` to your `main` branch will **automatically re-deploy** to Render! 🚀

---

## Questions?
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
