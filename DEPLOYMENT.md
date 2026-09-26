# 🚀 ORBITUNE Deployment Guide (Vercel & Render)

This guide covers deploying the **ORBITUNE** project:
- **Frontend 1 (Next.js Homepage)** → [Vercel](https://vercel.com)
- **Frontend 2 (React/Vite 3D Dashboard)** → [Vercel](https://vercel.com)
- **Backend (FastAPI + AI/ML Engine)** → [Render](https://render.com)

---

## 🔒 Security & Sensitive Data Checklist

1. **Never commit `.env` to Git.**
   - All real API keys (`GEMINI_API_KEY`, Supabase keys) are ignored by `.gitignore`.
   - Use [`.env.example`](file:///e:/ORBITUNE-main/ORBITUNE-main/.env.example) as your template when configuring environment variables on Vercel and Render dashboards.
2. **Audio & Media Assets**:
   - All 26 spatial tracks and album artwork stream directly from your Supabase storage buckets (`orbitune-audio` and `orbitune-audio-2`).
   - Heavy local media folders (`spatial/`, `thumbnails/`, `READY_FOR_SUPABASE/`, `READY_FOR_SUPABASE_BATCH2/`, and `*.wav`) are in `.gitignore`. Your GitHub push will remain clean, lightweight, and fast.

---

## 1. Deploy Backend on Render

1. Log in to [Render.com](https://render.com).
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository.
4. Configure the Web Service settings:
   - **Name**: `orbitune-backend`
   - **Root Directory**: leave blank (or `.`)
   - **Environment**: `Python`
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     python -m uvicorn BACKEND.src.app:app --host 0.0.0.0 --port $PORT
     ```
5. Add **Environment Variables** in Render:
   - `PYTHON_VERSION`: `3.12.0`
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key)*
   - `CORS_ORIGINS`: `https://your-homepage.vercel.app,https://your-dashboard.vercel.app` *(add after deploying Vercel apps)*
6. Click **Deploy Web Service**.
   - Your API will be live at: `https://orbitune-backend.onrender.com` (Health check endpoint: `/health`).

*(Note: The included `render.yaml` file in the root directory can also be used with Render's **Blueprints** feature for automatic setup).*

---

## 2. Deploy Dashboard on Vercel

1. In [Vercel Dashboard](https://vercel.com), click **Add New...** → **Project**.
2. Select your ORBITUNE Git repository.
3. Configure the Project:
   - **Project Name**: `orbitune-dashboard`
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select:
     ```text
     FRONTEND/dashboard/orbitune-sonic-verse-main
     ```
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add **Environment Variables**:
   - `VITE_API_URL`: `https://orbitune-backend.onrender.com` *(your Render backend URL)*
   - `VITE_HOMEPAGE_URL`: `https://your-orbitune-homepage.vercel.app` *(your Homepage Vercel URL)*
5. Click **Deploy**.

---

## 3. Deploy Homepage on Vercel

1. In [Vercel Dashboard](https://vercel.com), click **Add New...** → **Project**.
2. Select your ORBITUNE Git repository again.
3. Configure the Project:
   - **Project Name**: `orbitune-homepage`
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click *Edit* and select:
     ```text
     FRONTEND/orbitune-homepage
     ```
   - **Build Command**: `npm run build`
4. Add **Environment Variables**:
   - `NEXT_PUBLIC_DASHBOARD_URL`: `https://orbitune-dashboard.vercel.app/dashboard` *(your Dashboard Vercel URL)*
5. Click **Deploy**.

---

## 4. Verification & Testing

- ✅ **Next.js Homepage**: `npm run build` builds clean static pages.
- ✅ **Vite 3D Dashboard**: `npm run build` bundles all 26 Supabase tracks cleanly into `dist/`.
- ✅ **FastAPI Backend**: Health checks enabled on `/` and `/health`, and dynamic CORS configured for Vercel domains.
