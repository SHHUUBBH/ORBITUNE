# 🚀 ORBITUNE - Complete Run Guide

## Quick Start (Single Command)

Run the entire project with **ONE command**:

```powershell
.\START.ps1
```

That's all you need! The script handles everything automatically.

---

## 📖 What is ORBITUNE?

ORBITUNE is a 3D audio platform with AI companion that:
- ✅ Converts YouTube music to immersive 3D spatial audio
- ✅ AI chatbot (Gemini Flash 2.0) for music recommendations
- ✅ Real-time audio visualization
- ✅ Professional stem separation (vocals, drums, bass, instruments)
- ✅ Dual mode: Search YouTube or Chat with AI

---

## 🎯 Prerequisites

Make sure you have these installed:

1. **Python 3.8+** → [Download](https://www.python.org/downloads/)
2. **Node.js 16+** → [Download](https://nodejs.org/)
3. **Windows PowerShell** (pre-installed on Windows)

---

## 🏃‍♂️ How to Run

### Option 1: Full Startup (Recommended)
```powershell
.\START.ps1
```
- Installs all dependencies automatically
- Starts backend (port 8000) and frontend (port 5173)
- Opens browser to dashboard
- First run takes 3-5 minutes

### Option 2: Fast Startup (Skip Dependencies)
```powershell
.\START.ps1 -SkipDependencies
```
- Use after first run
- Faster startup (~30 seconds)

### Option 3: Backend Only
```powershell
.\START.ps1 -BackendOnly
```

### Option 4: Frontend Only
```powershell
.\START.ps1 -FrontendOnly
```

---

## 🌐 Access Points

Once running, open these URLs:

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:5173/dashboard |
| **Backend API** | http://127.0.0.1:8000 |
| **API Docs** | http://127.0.0.1:8000/docs |
| **Health Check** | http://127.0.0.1:8000/api/chatbot/health |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Tab** | Switch between Search 🔍 and Chat 💬 modes |
| **Ctrl+Space** | Toggle Debug Panel (hidden by default) |
| **Enter** | Send message/search |

---

## 🎮 How to Use

### Search Mode 🔍
1. Press **Tab** to enter Search Mode
2. Type a song name (e.g., "Bohemian Rhapsody")
3. Select from YouTube suggestions
4. Wait 30-60 seconds for 3D processing
5. Play and enjoy spatial 3D audio!

### Chat Mode 💬
1. Press **Tab** to enter Chat Mode
2. Tell AI your mood (e.g., "I'm feeling energetic!")
3. Get personalized recommendations
4. Ask about artists, genres, or music
5. AI learns your preferences over time

### Debug Panel 🛠️
- Press **Ctrl+Space** to show/hide
- See real-time audio diagnostics
- Check network status
- View buffering info
- Perfect for troubleshooting

---

## 🛑 How to Stop

1. **Close** the Backend and Frontend PowerShell windows
   - OR -
2. Press **Ctrl+C** in each window

---

## 🔧 What Was Fixed

### YouTube Download Issues (HTTP 403 Errors)

**Problem:** YouTube was blocking downloads with "Precondition check failed" and "HTTP 403: Forbidden" errors.

**Solution:** Added advanced yt-dlp bypass configuration:
- ✅ Browser user-agent spoofing
- ✅ Android player client fallback
- ✅ Proper HTTP headers
- ✅ Skip problematic extractors
- ✅ Latest yt-dlp version (2025.11.12)

**Files Modified:**
- `AI-ML/config.py` - Added bypass options to YTDLP_OPTIONS
- `AI-ML/audio_processor/youtube_downloader.py` - Updated search and info functions

**Result:** YouTube downloads now work perfectly without 403 errors!

---

## 📁 Project Structure

```
ORBITUNE/
├── START.ps1                    ⭐ Run this file!
├── RUN_GUIDE.md                 📖 This guide
├── AI-ML/                       🤖 AI & Audio Processing
│   ├── audio_processor/         
│   │   ├── youtube_downloader.py  (Fixed!)
│   │   ├── source_separator.py
│   │   └── orbitune_final.py
│   ├── chatbot/                 💬 Gemini AI chatbot
│   ├── models/                  🎵 Audio models
│   ├── venv/                    🐍 Python environment (auto-created)
│   ├── config.py                (Fixed!)
│   └── requirements.txt
├── BACKEND/                     🔧 FastAPI Server
│   └── src/
│       ├── app.py               Main API
│       ├── routes/              API endpoints
│       └── services/            Business logic
├── FRONTEND/                    ⚛️ React Dashboard
│   └── dashboard/
│       └── orbitune-sonic-verse-main/
│           ├── src/             React components
│           └── package.json
├── STORAGE/                     💾 Audio files (auto-created)
│   ├── raw_audio/               Downloaded audio
│   ├── processed/               Separated stems
│   ├── spatial/                 3D audio output
│   └── thumbnails/              Song images
└── .env                         🔑 API keys
```

---

## 🐛 Troubleshooting

### Issue: Backend Won't Start

**Check Python:**
```powershell
python --version
```
Should be 3.8 or higher.

**Check Port 8000:**
```powershell
netstat -ano | findstr :8000
```
If occupied:
```powershell
taskkill /PID <PID_NUMBER> /F
```

### Issue: Frontend Won't Start

**Check Node.js:**
```powershell
node --version
```
Should be 16 or higher.

**Reinstall Dependencies:**
```powershell
cd FRONTEND\dashboard\orbitune-sonic-verse-main
Remove-Item -Recurse -Force node_modules
npm install
cd ..\..\..
.\START.ps1
```

### Issue: YouTube Download Fails

**Already Fixed!** The latest version includes:
- ✅ Updated yt-dlp to version 2025.11.12
- ✅ Added bypass configurations
- ✅ Browser user-agent spoofing
- ✅ Android player client fallback

**If still failing:**
1. Restart backend: Close backend window → Run `.\START.ps1 -BackendOnly`
2. Try a different song
3. Check if video is age-restricted or region-locked

### Issue: Chatbot Not Responding

**Test Health:**
```powershell
curl http://127.0.0.1:8000/api/chatbot/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "gemini_available": true,
  "components": {
    "intent_detector": true,
    "user_profiler": true,
    "conversation_memory": true,
    "response_generator": true
  }
}
```

**Check .env File:**
```powershell
cat .env
```
Should contain:
```
GEMINI_API_KEY=your_api_key_here
```

### Issue: 3D Audio Processing Slow

**Normal Processing Time:**
- Download: 10-20 seconds
- Stem Separation: 20-40 seconds
- 3D Processing: 10-20 seconds
- **Total: 40-80 seconds**

**Speed Tips:**
- Use GPU if available (auto-detected)
- Choose shorter songs (under 5 minutes)
- Close other heavy applications

### Issue: Audio Not Playing

**Check Debug Panel:**
1. Press **Ctrl+Space**
2. Look for errors in debug info
3. Check network status
4. Verify audio URL is accessible

**Check Browser Console:**
1. Press **F12**
2. Go to Console tab
3. Look for error messages

---

## 💡 Pro Tips

1. **Use headphones** - Best 3D audio experience
2. **Be patient** - First download takes longer (model loading)
3. **Try Chat Mode** - AI gives great recommendations
4. **Use Tab key** - Quick mode switching
5. **Check logs** - Backend/Frontend windows show detailed info
6. **GPU recommended** - Much faster processing

---

## 🎨 Features

### Core Features
- ✅ YouTube to 3D Audio conversion
- ✅ AI music companion (Gemini Flash 2.0)
- ✅ Professional stem separation (Demucs)
- ✅ Real-time audio visualization
- ✅ Mood-based recommendations
- ✅ Natural language conversations

### UI/UX Features
- ✅ Glassmorphic design
- ✅ Smooth animations
- ✅ Responsive layout
- ✅ Particle effects
- ✅ Keyboard shortcuts
- ✅ Hidden debug panel

---

## 🔑 Environment Variables

The `.env` file is auto-created with a default API key. To use your own:

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Edit `.env` file:
   ```
   GEMINI_API_KEY=your_new_api_key_here
   ```
3. Restart backend: `.\START.ps1 -BackendOnly -SkipDependencies`

---

## 📊 System Requirements

### Minimum
- **CPU:** Dual-core processor
- **RAM:** 4 GB
- **Disk:** 2 GB free space
- **OS:** Windows 10/11
- **Internet:** Stable connection

### Recommended
- **CPU:** Quad-core or better
- **RAM:** 8 GB or more
- **GPU:** NVIDIA GPU with CUDA (for faster processing)
- **Disk:** 5 GB free space (for multiple songs)

---

## 🆘 Support

### Check These First
1. ✅ Python and Node.js installed?
2. ✅ Ports 8000 and 5173 available?
3. ✅ Internet connection stable?
4. ✅ Backend window shows no errors?
5. ✅ Frontend window shows no errors?

### Still Having Issues?
1. Check backend logs (backend PowerShell window)
2. Check frontend logs (frontend PowerShell window)
3. Open browser console (F12)
4. Review this guide's troubleshooting section
5. Try with a different song

---

## 🎉 Summary

### To run ORBITUNE:
1. Open PowerShell
2. Navigate to ORBITUNE directory
3. Run: `.\START.ps1`
4. Wait for browser to open
5. Enjoy 3D audio with AI companion!

### Single command, zero hassle! 🚀

**Everything is automated:**
- ✅ Virtual environment creation
- ✅ Dependency installation
- ✅ Backend startup (Python/FastAPI)
- ✅ Frontend startup (React/Vite)
- ✅ Health checks
- ✅ Browser launch

---

## 📝 Changelog

### Latest Update (Fixed)
- ✅ **YouTube downloads now working** (Fixed HTTP 403 errors)
- ✅ Updated yt-dlp to latest version (2025.11.12)
- ✅ Added bypass configuration for YouTube restrictions
- ✅ Browser user-agent spoofing
- ✅ Android player client fallback
- ✅ Improved error handling

### Previous Features
- ✅ One-command startup script
- ✅ Hidden debug panel (Ctrl+Space)
- ✅ Gemini Flash 2.0 integration
- ✅ Tab key mode switching
- ✅ Real-time visualization
- ✅ Automatic browser launch

---

## 🎵 Enjoy ORBITUNE!

**Made with ❤️ by the ORBITUNE Team**

Experience music in a whole new dimension! 🌌🎧✨
