# Vercel Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Current Status

**Frontend:**
- ✅ Next.js 15.2.4
- ✅ React 19
- ✅ TypeScript 5
- ✅ All dependencies specified in `package.json`
- ✅ `vercel.json` configured

**Issues Found:**
- ❌ Hardcoded `localhost:8000` in frontend code
- ❌ No environment variable configuration
- ❌ Backend API URL needs to be configurable

### 🔧 Required Changes

#### 1. Environment Variables Setup

**For Vercel Deployment:**
1. Go to your Vercel project settings
2. Navigate to "Environment Variables"
3. Add the following:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api-url.com
   ```

**For Local Development:**
Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 2. Backend Deployment (Separate from Vercel)

**Important:** Vercel only hosts frontend/static sites. Your FastAPI backend needs separate hosting.

**Recommended Backend Hosting Options:**
1. **Railway** - Easy Python/FastAPI deployment
2. **Render** - Free tier available for Python apps
3. **Heroku** - Popular choice for Python backends
4. **DigitalOcean App Platform** - Simple deployment
5. **AWS/GCP/Azure** - Enterprise solutions

### 📝 Step-by-Step Deployment

#### Frontend (Vercel)

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Update API URLs in Frontend**:
   - The `lib/config.ts` file has been created to use environment variables
   - Update all fetch calls to use `config.apiUrl` instead of hardcoded `localhost:8000`

3. **Deploy to Vercel**:
   ```bash
   cd frontend
   vercel
   ```
   
   Or connect your GitHub repo to Vercel dashboard for automatic deployments.

4. **Set Environment Variables in Vercel**:
   - Project Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_URL` with your backend URL

#### Backend (Separate Hosting)

1. **Prepare Backend for Deployment**:
   - Ensure `backend/requirements.txt` is complete
   - Create a production-ready configuration
   - Set up environment variables (API keys, etc.)

2. **Deploy Backend** (example with Railway):
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   
   # Deploy
   cd backend
   railway up
   ```

3. **Get Backend URL**:
   - After deployment, copy your backend URL (e.g., `https://your-app.railway.app`)
   - Update `NEXT_PUBLIC_API_URL` in Vercel with this URL

### 🔐 Environment Variables Required

#### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL` - Backend API URL

#### Backend (Backend Hosting)
- `OPENAI_API_KEY` - Your OpenAI API key
- `PORT` - Server port (usually auto-set by hosting)
- `CORS_ORIGINS` - Frontend URL(s) for CORS

### 📦 Dependencies Verification

**Frontend Dependencies:**
- ✅ Next.js: 15.2.4
- ✅ React: ^19
- ✅ TypeScript: ^5
- ✅ All UI dependencies specified
- ✅ Build tools configured

**Backend Dependencies:**
- ✅ FastAPI: >=0.104.0
- ✅ Uvicorn: >=0.24.0
- ✅ Pydantic: >=2.0.0
- ✅ OpenAI: >=1.0.0

### 🚨 Important Notes

1. **Backend Must Be Deployed Separately**
   - Vercel does NOT support Python/FastAPI backends
   - You need separate hosting for `backend/`

2. **CORS Configuration**
   - Update `backend/config/settings.py` with your Vercel frontend URL
   - Add your production frontend URL to `CORS_ORIGINS`

3. **API Keys**
   - Never commit API keys to repository
   - Use environment variables in both frontend and backend

4. **Build Optimizations**
   - Frontend is configured for production builds
   - Images are unoptimized (can be optimized later)

### ✅ Post-Deployment Checklist

- [ ] Frontend deployed on Vercel
- [ ] Backend deployed on separate hosting
- [ ] Environment variables set in both services
- [ ] CORS configured correctly
- [ ] API endpoints tested
- [ ] Authentication working
- [ ] All test modules functional

### 🔄 Update Frontend Code

You need to update all API calls to use the config file. Here's what needs to be updated:

1. `frontend/app/login/page.tsx` - Login API call
2. `frontend/app/dashboard/layout.tsx` - Logout API call
3. `frontend/app/dashboard/prompt-injection/page.tsx` - Test endpoints
4. `frontend/app/dashboard/jailbreak/page.tsx` - Test endpoints
5. `frontend/app/dashboard/data-extraction/page.tsx` - Test endpoints

### 📊 Deployment Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Vercel        │         │   Backend Host   │
│   (Frontend)    │ ──────> │   (FastAPI)      │
│   Next.js App   │  HTTP   │   Python Server  │
│   Port: 3000    │         │   Port: 8000     │
└─────────────────┘         └──────────────────┘
      │                            │
      │                            │
      └────────────────────────────┘
           API Calls (REST)
```

### 🎯 Next Steps

1. Update frontend code to use `config.apiUrl`
2. Deploy backend to hosting service
3. Get backend URL
4. Set `NEXT_PUBLIC_API_URL` in Vercel
5. Update backend CORS settings
6. Test deployment
7. Monitor both services



