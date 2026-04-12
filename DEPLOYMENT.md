# AgriGuard - Render Deployment Guide

## Overview
This guide walks through deploying AgriGuard (full-stack React + Flask app) to Render.com

---

## Prerequisites
- GitHub account with repository pushed
- Render account (free tier available at render.com)
- MongoDB Atlas account (cloud MongoDB)

---

## Step 1: Prepare MongoDB Atlas

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free tier cluster
3. Create a database user:
   - Username: `agriguard`
   - Generate a password
4. Whitelist your IP (or allow all IPs for testing)
5. Get your connection string: `mongodb+srv://agriguard:PASSWORD@cluster.mongodb.net/smartcrop?retryWrites=true&w=majority`

---

## Step 2: Push to GitHub

From your local project directory:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

**Files added for deployment:**
- `Procfile` - Backend process definition
- `render.yaml` - Full-stack deployment config
- `frontend/.env.production` - Frontend production env vars
- `backend/app.py` - Updated with relative imports

---

## Step 3: Deploy on Render

### Option A: Using render.yaml (Recommended)

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Name: `agriguard`
5. Branch: `main`
6. Click **"Deploy"**
7. Render will automatically:
   - Build both services
   - Set up backend API
   - Build frontend SPA
   - Deploy frontend

### Option B: Manual Deployment

#### Deploy Backend:
1. Click **"New +"** → **"Web Service"**
2. Select your GitHub repository
3. **Name:** `agriguard-backend`
4. **Runtime:** Python 3.12
5. **Build Command:** `cd backend && pip install -r requirements.txt`
6. **Start Command:** `cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
7. **Environment Variables:**
   ```
   MONGO_URI=mongodb+srv://agriguard:YOUR_PASSWORD@cluster.mongodb.net/smartcrop?retryWrites=true&w=majority
   OPENWEATHER_API_KEY=YOUR_API_KEY_HERE
   ```
8. Click **"Deploy"**

#### Deploy Frontend:
1. Click **"New +"** → **"Static Site"**
2. Select your GitHub repository
3. **Name:** `agriguard-frontend`
4. **Build Command:** `cd frontend && npm install && npm run build`
5. **Publish Directory:** `frontend/dist`
6. **Environment Variables:**
   ```
   VITE_API_URL=https://agriguard-backend.onrender.com/api
   ```
7. Click **"Deploy"**

---

## Step 4: Verification

### Test Backend:
```
https://agriguard-backend.onrender.com/
```
Should show: `{"status": "running", "message": "Smart Crop API is healthy"}`

### Test Login:
```bash
POST https://agriguard-backend.onrender.com/api/auth/login
Content-Type: application/json

{
  "username": "test",
  "password": "test123"
}
```

### Test Frontend:
Open `https://agriguard-frontend.onrender.com` in browser

---

## Important Notes

### Database Initialization
The test users won't auto-seed on Render. SSH into backend and run:
```bash
python backend/seed.py
```

Or create users through the frontend Sign Up page.

### MongoDB Database Name
Make sure your MONGO_URI points to the `smartcrop` database.

### Cold Starts
Free tier services sleep after 15 minutes of inactivity. First request will be slow (~30 seconds).

### API Timeout
If using free MongoDB, might hit timeouts. Consider upgrading for production.

---

## Troubleshooting

### Backend won't start
- Check logs: Go to service → Logs
- Verify Python version: `python3.12`
- Ensure gunicorn in requirements.txt

### Frontend shows blank page
- Check browser console (F12)
- Verify VITE_API_URL is set correctly
- Check frontend build succeeded in logs

### 401 Unauthorized on login
- Seed test users: `python backend/seed.py` in SSH
- MongoDB connection issue: Check MONGO_URI in logs

---

## Custom Domain (Optional)

1. In Render dashboard, go to your service
2. Settings → Custom Domain
3. Add your domain
4. Follow DNS instructions

---

## Cost Summary
- **Free Tier:**
  - Web Service: 50 hours/month (0.5 vCPU, 512MB RAM)
  - Static Site: Free
  - MongoDB Atlas: Free tier (512MB)
  - Total: Free (with limitations)

---

## Next Steps for Production
- [ ] Upgrade MongoDB to paid tier (M2+)
- [ ] Use Render paid plans for guaranteed uptime
- [ ] Set up HTTPS (auto-enabled on Render)
- [ ] Add real domain
- [ ] Set up email notifications
- [ ] Enable CORS restrictions
