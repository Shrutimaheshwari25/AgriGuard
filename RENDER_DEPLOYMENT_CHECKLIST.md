# 🚀 DEPLOYMENT CHECKLIST - Render.com

## ✅ What's Ready
All deployment files have been created and pushed to GitHub:
- ✅ `Procfile` - Backend startup configuration  
- ✅ `render.yaml` - Full-stack deployment definition
- ✅ `frontend/.env.production` - Production environment variables
- ✅ `backend/seed.py` - Database initialization script
- ✅ `DEPLOYMENT.md` - Full deployment guide

---

## 📋 DEPLOYMENT STEPS

### Step 1: Create MongoDB Atlas Database (5 mins)

1. Go to **https://www.mongodb.com/cloud/atlas**
2. Sign up (free) or login
3. Click **"Create" → Database**
4. Choose **FREE M0 Sandbox** → Create
5. **Create database user:**
   - Username: `agriguard`
   - Password: (save this!)
   - Click **"Create User"**
6. **Network Access:**
   - Click **"Network Access"**
   - Click **"Add IP Address"**
   - Select **"Allow access from anywhere"** (for testing)
   - Click **"Confirm"**
7. **Get Connection String:**
   - Go back to **Databases** → Click **"Connect"**
   - Choose **"Drivers"** → **Python**
   - Copy the connection string (looks like):
     ```
     mongodb+srv://agriguard:PASSWORD@cluster0.xxxxx.mongodb.net/smartcrop?retryWrites=true&w=majority
     ```
   - Replace `PASSWORD` with your actual password

---

### Step 2: Deploy on Render (10 mins)

#### Option A: Using render.yaml (Easiest)

1. Go to **https://dashboard.render.com**
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account (if not already connected)
4. Select **AgriGuard** repository
5. Click **"Connect"**
6. Enter **Service Group Name:** `agriguard`
7. Click **"Create Blueprint"**
8. Wait for deployment to complete (5-10 minutes)

#### Option B: Manual Deployment

**Deploy Backend:**
1. Go to **https://dashboard.render.com**
2. Click **"New +"** → **"Web Service"**
3. Select **AgriGuard** repo → **"Connect"**
4. Fill in:
   - Name: `agriguard-backend`
   - Runtime: `Python 3.12`
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
5. Click **"Environment"** tab
6. Add environment variables:
   - `MONGO_URI`: (Your MongoDB connection string)
   - `OPENWEATHER_API_KEY`: `452b067c745cea18b2f55ad3c23a7b1c` (or your own)
7. Click **"Create Web Service"**
8. Wait for deployment (3-5 mins)

**Deploy Frontend:**
1. Click **"New +"** → **"Static Site"**
2. Select **AgriGuard** repo → **"Connect"**
3. Fill in:
   - Name: `agriguard-frontend`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
4. Click **"Environment"** tab
5. Add environment variable:
   - `VITE_API_URL`: `https://agriguard-backend.onrender.com/api`
   - (Replace `agriguard-backend` with your actual backend service name)
6. Click **"Create Static Site"**
7. Wait for deployment (2-3 mins)

---

### Step 3: Initialize Database

After both services are deployed:

1. Go to **Backend service** → **"Shell"** tab
2. Run:
   ```bash
   cd backend && python seed.py
   ```
3. You should see:
   ```
   ✅ Created user 'test' (ID: ...)
   ✅ Created user 'demo' (ID: ...)
   ```

---

### Step 4: Test Deployment

#### Test Backend API
Open in browser:
```
https://agriguard-backend.onrender.com/
```
Should show:
```json
{
  "status": "running",
  "message": "Smart Crop API is healthy"
}
```

#### Test Frontend
Open in browser:
```
https://agriguard-frontend.onrender.com
```

#### Test Login
Use credentials:
- Email/Username: `test`
- Password: `test123`

---

## 🔗 YOUR DEPLOYMENT URLS

Once deployed, you'll have:

```
Backend API:    https://agriguard-backend.onrender.com/api
Frontend App:   https://agriguard-frontend.onrender.com
```

---

## ⚠️ Important Notes

### Cold Starts
- Free tier services sleep after 15 minutes
- First request will be slow (~30 seconds)
- No cold starts on paid plans

### Database
- Make sure MongoDB connection string database is `smartcrop`
- Test user credentials won't auto-seed; run `seed.py` in shell

### Memory & CPU
- Free tier: 512MB RAM, 0.5 vCPU
- If getting "crashed", upgrade to Starter tier ($7/month)

### Logs
- Backend logs: Dashboard → Service → Logs
- Frontend logs: Dashboard → Service → Logs

---

## 🆘 Troubleshooting

### Backend Service Won't Deploy
- Check: **Logs** tab for errors
- Verify: `gunicorn` is in `requirements.txt`
- Ensure: Python version is 3.12

### Frontend Blank Page
- Open browser **DevTools (F12)** → **Console**
- Check for API URL errors
- Verify `VITE_API_URL` is set correctly

### Login Returns 401
- SSH into backend service
- Run: `python backend/seed.py`
- Verify MongoDB connection

### Services Keep Crashing
- Check memory usage in Logs
- Upgrade to Starter tier
- Check for infinite loops in code

---

## 💰 Free Tier Limitations
- **Web Services:** ~0.5 vCPU, 512MB RAM (sleeps when inactive)
- **Static Sites:** Unlimited bandwidth
- **MongoDB:** 512MB free tier (enough for testing)

### Upgrade Path (Optional)
- Backend: Starter ($7/month) → Production ($35+/month)
- MongoDB: M2 ($57/month)

---

## 📝 Next Steps

1. Create MongoDB Atlas cluster
2. Get your MongoDB connection string
3. Deploy on Render (Option A or B)
4. Initialize database
5. Test both frontend and backend
6. Share your URLs!

---

## ✨ You're All Set!

Your full-stack app is now deployed on Render! 🎉

Questions? Check the detailed guide in `DEPLOYMENT.md`

